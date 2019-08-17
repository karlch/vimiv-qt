Feature: Chain commands together.

    Background:
        Given I open a directory with 5 paths

    Scenario: Chain two commands together.
        When I run scroll down && scroll down
        Then the library row should be 3

    Scenario: Chain three commands together.
        When I run scroll down && scroll down && scroll down
        Then the library row should be 4

    Scenario: Fail first of two chained commands
        When I run something wrong && scroll down
        Then the library row should be 1
        And the message
            'something: unknown command for mode library'
            should be displayed

    Scenario: Fail second of two chained commands
        When I run scroll down && something wrong
        Then the library row should be 2
        And the message
            'something: unknown command for mode library'
            should be displayed

    Scenario: Fail second of three chained commands
        When I run scroll down && something wrong && scroll down
        Then the library row should be 2
        And the message
            'something: unknown command for mode library'
            should be displayed
