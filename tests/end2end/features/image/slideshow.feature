Feature: Play a slideshow.

    Scenario: Start playing slideshow
        Given I open any image
        When I run slideshow
        Then the center status should include slideshow
        And the slideshow should be playing

    Scenario: Start and stop slideshow
        Given I open any image
        When I run slideshow
        And I run slideshow
        Then the slideshow should not be playing

    Scenario: Set slideshow delay via setting
        Given I open any image
        When I run set slideshow.delay 4
        Then the slideshow delay should be 4.0

    Scenario: Set slideshow delay via count
        Given I open any image
        When I run 5slideshow
        Then the slideshow delay should be 5.0

    Scenario: Slideshow updates the displayed image
        Given I open 5 images
        And I forcefully set the slideshow delay to 10ms
        When I run slideshow
        And I let the slideshow run 2 times
        Then the image should have the index 3
        And the left status should include 03

    Scenario: Start slideshow upon startup
        Given I open 5 images with --command slideshow
        Then the slideshow should be playing

    Scenario: Leave slideshow when image is unfocused
        Given I open any image
        When I run slideshow
        And I unfocus the image
        Then the slideshow should not be playing
