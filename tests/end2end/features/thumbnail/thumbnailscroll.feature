Feature: Scroll in thumbnail mode.

    Scenario: Scroll to next thumbnail
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll right
        Then the thumbnail number 2 should be selected

    Scenario: Scroll with count
        Given I open 10 images
        And I enter thumbnail mode
        When I run 2scroll right
        Then the thumbnail number 3 should be selected

    Scenario: Do not wrap when scrolling back
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll left
        Then the thumbnail number 1 should be selected

    Scenario: Do not move when scrolling up in first row
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll right
        And I run scroll up
        Then the thumbnail number 2 should be selected

    Scenario: Scroll down
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll down
        # Under defaults we have a window width of 400px and a thumbnail width
        # of 128px with padding of 20px. This means we have exactly 2
        # thumbnails per row.
        Then the thumbnail number 3 should be selected

    Scenario: Scroll down and back up
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll down
        And I run scroll up
        Then the thumbnail number 1 should be selected

    Scenario: Do not move to last thumbnail when scrolling down in final row
        Given I open 10 images
        And I enter thumbnail mode
        When I run 50scroll down
        Then the thumbnail number 9 should be selected

    Scenario: Follow library mode
        Given I open 10 images
        And I enter thumbnail mode
        When I enter library mode
        And I run goto 5
        Then the thumbnail number 5 should be selected

    Scenario: Crash when scrolling empty thumbnail list
        Given I start vimiv
        When I enter thumbnail mode
        And I run scroll down
        Then no crash should happen
        And the message
            'scroll: Thumbnail list is empty'
            should be displayed

    Scenario: Remove last thumbnail
        Given I open any image
        When I enter thumbnail mode
        And I run delete %
        And I wait for the working directory handler
        Then there should be 0 thumbnails

    Scenario: Scroll to end of line
        Given I open 10 images
        And I enter thumbnail mode
        When I run end-of-line
        Then the thumbnail number 2 should be selected

    Scenario: Scroll to first of line
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll right
        And I run first-of-line
        Then the thumbnail number 1 should be selected

    Scenario Outline: Move the view
        Given I open 10 images
        And I enter thumbnail mode
        When I run scroll half-page-down
        And I run move-view <position>
        # Simple test if we don't scroll and no crash happens
        Then no crash should happen

        Examples:
            | position |
            | top      |
            | center   |
            | bottom   |

    Scenario: Crash on scroll when updating scroll_to_center setting
        Given I open 10 images
        And I enter thumbnail mode
        When I run set scroll_to_center!
        And I run scroll down
        Then no crash should happen
