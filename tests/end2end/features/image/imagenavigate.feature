Feature: Navigating through the displayed images

    Background:
        Given I open 5 images

    Scenario: Move to next image
        When I run next
        Then the image should have the index 2

    Scenario: Move to next image and back
        When I run next
        And I run prev
        Then the image should have the index 1

    Scenario: Move to last image by wrapping :prev
        When I run prev
        Then the image should have the index 5

    Scenario: Wrap back and forth
        When I run prev
        And I run next
        Then the image should have the index 1

    Scenario: Move to last image with goto
        When I run goto -1
        Then the image should have the index 5

    Scenario: Move to last image and back to first with goto
        When I run goto -1
        And I run goto 1
        Then the image should have the index 1

    Scenario: Move to specific image using goto with count
        When I run 3goto 1
        Then the image should have the index 3
