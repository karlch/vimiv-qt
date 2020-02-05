Feature: Create and run aliases.

    Scenario: Create and run an alias.
        Given I start vimiv
        When I run alias mycount count
        And I run mycount
        Then the count should be 1

    Scenario: Create an alias and run it with arguments.
        Given I start vimiv
        When I run alias mycount count
        And I run mycount --number=5
        Then the count should be 5

    Scenario: Create and run an alias with arguments.
        Given I start vimiv
        When I run alias count-three 'count --number=3'
        And I run count-three
        Then the count should be 3

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
        Then the directory other_directory should exist
