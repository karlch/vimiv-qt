Feature: Chain commands together.

    Background:
        Given I start vimiv

    Scenario: Chain two commands together.
        When I run count && count
        Then the count should be 2

    Scenario: Chain three commands together.
        When I run count && count && count
        Then the count should be 3

    Scenario: Chain commands with count together.
        When I run 2count && 3count
        Then the count should be 5

    Scenario: Fail first of two chained commands
        When I run something wrong && count
        Then the count should be 0
        And the message
            'something: unknown command for mode library'
            should be displayed

    Scenario: Fail second of two chained commands
        When I run count && something wrong
        Then the count should be 1
        And the message
            'something: unknown command for mode library'
            should be displayed

    Scenario: Fail second of three chained commands
        When I run count && something wrong && count
        Then the count should be 1
        And the message
            'something: unknown command for mode library'
            should be displayed

    Scenario: Run an alias of chained commands
        When I run alias double-count count \&\& count
        And I run double-count
        # Run twice as running once also works if the alias is only aliased to the first
        # command and the second command is executed right after the alias command
        And I run double-count
        Then the count should be 4

    Scenario: Run a chain of aliases where each alias consists of a chain of commands
        When I run alias double-count count \&\& count
        When I run alias triple-count count \&\& count \&\&count
        And I run double-count && double-count && triple-count
        Then the count should be 7
