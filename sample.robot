*** Settings ***

Library      api_library.py
Resource     endpoints.resource

*** Test Cases ***

Multiple Accounts

    Use Account    user1    password1

    Make GET Request
    ${GET_USER}
    100

    Use Account    user2    password2

    Make GET Request
    ${GET_USER}
    200

    Use Previous Account

    Make GET Request
    ${GET_USER}
    100