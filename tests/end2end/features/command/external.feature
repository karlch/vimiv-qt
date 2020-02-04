Feature: Running external commands.

    Background:
        Given I start vimiv

    Scenario: Run an external command.
        When I run !touch file
        And I wait for the command to complete
        Then the file file should exist
        And no message should be displayed

    Scenario: Fail an external command.
        When I run !not-a-shell-command
        And I wait for the command to complete
        Then the message
            'Error running 'not-a-shell-command': command not found or not executable'
            should be displayed

    @flaky
    Scenario: Pipe directory to vimiv.
        When I create the directory 'new_directory'
        And I run !ls |
        And I wait for the command to complete
        Then the working directory should be new_directory

    Scenario: Fail piping to vimiv.
        When I run !ls |
        And I wait for the command to complete
        Then the message
            'ls: No paths from pipe'
            should be displayed

    Scenario: Use spawn with sub-shell
        When I run spawn echo anything > test.txt
        And I wait for the command to complete
        Then the file test.txt should exist
