Feature: Handling symbolic links

    Scenario: Open real path when opening symlink
        Given I open the symlink test directory
        When I run open lnstem
        Then the working directory should be stem

    Scenario: Crash when searching in symlinked directory
        Given I open the symlink test directory
        When I run open lnstem
        And I run search
        And I press 'k'
        Then no crash should happen

    Scenario: Do not load path pointed to by symlink into filelist
        Given I open the symlink image test directory
        When I run open-selected --close
        Then the filelist should contain 1 images
