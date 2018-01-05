Feature: Scroll in thumbnail mode.

    Background:
        Given I open 10 images
        And I enter thumbnail mode

    Scenario: Scroll to next thumbnail
        When I run scroll right
        Then the thumbnail number 2 should be selected

    Scenario: Scroll with count
        When I run 2scroll right
        Then the thumbnail number 3 should be selected

    Scenario: Do not wrap when scrolling back
        When I run scroll left
        Then the thumbnail number 1 should be selected

    Scenario: Do not move when scrolling up in first row
        When I run scroll right
        And I run scroll up
        Then the thumbnail number 2 should be selected

    Scenario: Scroll down
        When I run scroll down
        # Under defaults we have a window width of 400px and a thumbnail width
        # of 128px with padding of 20px. This means we have exactly 2
        # thumbnails per row.
        Then the thumbnail number 3 should be selected

    Scenario: Scroll down and back up
        When I run scroll down
        And I run scroll up
        Then the thumbnail number 1 should be selected

    Scenario: Do not move to last thumbnail when scrolling down in final row
        When I run 50scroll down
        Then the thumbnail number 9 should be selected
