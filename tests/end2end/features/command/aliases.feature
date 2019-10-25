Feature: Create and run aliases.

    Scenario: Create and run an alias.
        Given I start vimiv
        When I run alias new_next next
        And I run new_next
        # If the command would not exist, we would see an error message
        Then no message should be displayed

    Scenario: Create an alias and run it with arguments.
        Given I start vimiv
        When I run alias new_goto goto
        And I run new_goto 0
        Then no message should be displayed

    Scenario: Create and run an alias with arguments.
        Given I start vimiv
        When I run alias start goto 0
        And I run start
        Then no message should be displayed

    Scenario: Do not overwrite existing commands with alias.
        Given I start vimiv
        When I run alias quit scroll
        Then the alias quit should not exist
        And the message
            'alias: Not overriding default command quit'
            should be displayed

    Scenario: Alias to an external command
        Given I start vimiv
        When I run alias listdir !ls
        And I run bind zzz listdir
        And I press zzz
        Then no message should be displayed

    Scenario: Alias including wildcards
        Given I open a directory with 1 paths
        When I run alias copythis '!cp -r \% other_directory'
        And I run copythis
        And I wait for the command to complete
        Then the directory other_directory should exist
