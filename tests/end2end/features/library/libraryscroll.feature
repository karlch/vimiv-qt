Feature: Scrolling the library.

    Scenario: Scroll up and down.
        Given I open a directory with 5 paths
        When I run scroll down
        And I run scroll down
        And I run scroll up
        Then the library row should be 2

    Scenario: Crash when scrolling empty directory.
        Given I open any directory
        When I run scroll down
        And I run scroll up
        Then no crash should happen
        And the message
            'scroll: Directory is empty'
            should be displayed

    Scenario: Crash when selecting file in empty directory.
        Given I open any directory
        When I run scroll right
        Then no crash should happen

    Scenario: Enter directory
        Given I open a directory with 1 paths
        When I run scroll right
        Then the working directory should be child_01

    Scenario: Enter and leave directory remembering position
        Given I open a directory with 2 paths
        When I run scroll down
        And I run scroll right
        And I run scroll left
        Then the library row should be 2

    Scenario: Set position to child directory when opening parent
        Given I open a directory with 2 paths
        When I run open child_02
        And I run scroll left
        Then the library row should be 2

    Scenario: Crash when entering directory without permission
        Given I open a directory for which I do not have access permissions
        Then no crash should happen

    Scenario: Scroll and open the selected image
        Given I open a directory with 2 images
        When I run scroll down --open-selected
        Then the library row should be 2
        And the image should have the index 2

    Scenario: Select specific image and open it
        Given I open a directory with 4 images
        When I run goto 3 --open-selected
        Then the library row should be 3
        And the image should have the index 3

    Scenario: Do not leave library mode with --open-selected
        Given I open a directory with 1 images
        When I run scroll down --open-selected
        And I run scroll down --open-selected
        Then the mode should be library

    Scenario: Follow image mode
        Given I open 2 images
        When I run next
        And I enter library mode
        Then the library row should be 2

    Scenario: Follow thumbnail mode
        Given I open 2 images
        When I enter thumbnail mode
        And I run goto 2
        Then the library row should be 2

    Scenario: Select row with goto using only count
        Given I open a directory with 2 paths
        When I run 2goto
        Then the library row should be 2

    Scenario: Display error when neither row nor count is passed to goto
        Given I open a directory with 2 paths
        When I run goto
        Then the message
            'goto: Either row or count is required'
            should be displayed

    Scenario: Keep correct selection when deleting images
        Given I open 5 images
        When I run goto 3
        And I run delete %
        And I wait for the working directory handler
        Then the library row should be 3

    Scenario: Keep correct selection when deleting directories
        Given I open a directory with 5 paths
        When I run goto 3
        And I run !rmdir %
        Then the library row should be 3

    Scenario: Keep correct selection when deleting last directory
        Given I open a directory with 5 paths
        When I run goto 5
        And I run !rmdir %
        Then the library row should be 4

    Scenario: Crash on goto in empty directory
        Given I start vimiv
        When I run goto 3
        Then no crash should happen
        And the message
            'goto: No path in list'
            should be displayed

    Scenario: Select first row of previously empty directory
        Given I open a directory with 1 paths
        When I run scroll right
        And I run scroll left
        And I create the directory 'child_01/child'
        And I run scroll right
        Then the library row should be 1

    Scenario: Scroll page down
        Given I open a directory with 50 paths
        When I run scroll page-down
        Then the library should be one page down

    Scenario: Scroll page down with count
        Given I open a directory with 50 paths
        When I run 2scroll page-down
        Then the library should be two pages down

    Scenario: Scroll page up
        Given I open a directory with 50 paths
        When I run scroll page-down
        And I run scroll page-up
        Then the library row should be 1

    Scenario: Scroll half page down
        Given I open a directory with 50 paths
        When I run scroll half-page-down
        Then the library should be half a page down

    Scenario: Scroll half page up
        Given I open a directory with 50 paths
        When I run scroll half-page-down
        And I run scroll half-page-up
        Then the library row should be 1

    Scenario Outline: Move the view
        Given I open a directory with 50 paths
        When I run scroll half-page-down
        And I run move-view <position>
        # Simple test if we don't scroll and no crash happens
        Then the library should be half a page down

        Examples:
            | position |
            | top      |
            | center   |
            | bottom   |

    Scenario: Scroll right and open selected stored image
        Given I open a directory with 3 images
        When I run scroll down
        When I run scroll left
        And I run scroll right --open-selected
        Then the library row should be 2
        And the image should have the index 2

    Scenario: Scroll left and clear the image list
        Given I open a directory with 3 images
        When I run scroll down --open-selected
        And I run scroll left --open-selected
        Then the image should have the index 0
