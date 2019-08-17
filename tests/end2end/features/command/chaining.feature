Feature: Chain commands together.

    Background:
        Given I open a directory with 5 paths

    Scenario: Chain two commands together.
        When I run scroll down && scroll down
        Then the library row should be 3

    Scenario: Chain three commands together.
        When I run scroll down && scroll down && scroll down
        Then the library row should be 4

    Scenario: Chain commands with count together.
        When I run 2scroll down && scroll down
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

    Scenario: Run an alias of chained commands
        When I run alias double_trouble scroll down \&\& scroll down
        And I run double_trouble
        # Run twice as running once also works if the alias is only aliased to scroll
        # down and the first scroll down is executed right after the alias command
        And I run double_trouble
        Then the library row should be 5

    Scenario: Run a chain of aliases where each alias consists of a chain of commands
        When I run alias double_trouble scroll down \&\& scroll down
        And I run alias reverse_double_trouble scroll up \&\& scroll up
        And I run double_trouble && double_trouble && reverse_double_trouble
        Then the library row should be 3
