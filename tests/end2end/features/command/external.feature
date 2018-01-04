Feature: Running external commands.

    Background:
        Given I start vimiv

    Scenario: Run an external command.
        When I run !touch file
        And I wait for the command to complete
        Then the file file should exist
        And no message should be displayed

    Scenario: Fail an external command.
        When I run !foo_bar_baz
        And I wait for the command to complete
        # Error message may vary between OS
        Then a message should be displayed

    Scenario: Pipe directory to vimiv.
        When I run !mkdir new_directory
        And I wait for the command to complete
        And I run !ls |
        And I wait for the command to complete
        Then the working directory should be new_directory

    Scenario: Fail piping to vimiv.
        When I run !ls |
        And I wait for the command to complete
        Then the message
            'ls: No paths from pipe'
            should be displayed
