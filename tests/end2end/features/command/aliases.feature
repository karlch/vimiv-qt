Feature: Create and run aliases.

    Background:
        Given I start vimiv

    Scenario: Create and run an alias.
        When I run alias new_next next
        And I run new_next
        # If the command would not exist, we would see an error message
        Then no message should be displayed

    Scenario: Create an alias and run it with arguments.
        When I run alias new_goto goto
        And I run new_goto 0
        Then no message should be displayed

    Scenario: Create and run an alias with arguments.
        When I run alias start goto 0
        And I run start
        Then no message should be displayed

    Scenario: Do not overwrite existing commands with alias.
        When I run alias quit scroll
        Then the alias quit should not exist
        And the message
            'alias: Not overriding default command quit'
            should be displayed
