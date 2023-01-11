Feature: Navigating through the displayed images

    Scenario: Move to next image
        Given I open 5 images
        When I run next
        Then the image should have the index 2

    Scenario: Move to next image and back
        Given I open 5 images
        When I run next
        And I run prev
        Then the image should have the index 1

    Scenario: Move to last image by wrapping :prev
        Given I open 5 images
        When I run prev
        Then the image should have the index 5

    Scenario: Wrap back and forth
        Given I open 5 images
        When I run prev
        And I run next
        Then the image should have the index 1

    Scenario: Move to last image with goto
        Given I open 5 images
        When I run goto -1
        Then the image should have the index 5

    Scenario: Move to last image and back to first with goto
        Given I open 5 images
        When I run goto -1
        And I run goto 1
        Then the image should have the index 1

    Scenario: Move to specific image using goto with count
        Given I open 5 images
        When I run 3goto
        Then the image should have the index 3

    Scenario: Crash on goto without images
        Given I start vimiv
        When I enter image mode
        When I run goto 3
        Then no crash should happen
        And the message
            'goto: No image in list'
            should be displayed
