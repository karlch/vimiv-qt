Feature: Handling symbolic links

    Background:
        Given I open the symlink test directory

    Scenario: Open real path when opening symlink
        When I run open lnstem
        Then the working directory should be stem

    Scenario: Crash when searching in symlinked directory
        When I run open lnstem
        And I run search
        And I press 'k'
        Then no crash should happen
