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
        Then the slideshow delay should be 4

    Scenario: Set slideshow delay via count
        Given I open any image
        When I run 5slideshow
        Then the slideshow delay should be 5

    Scenario: Slideshow updates the displayed image
        Given I open 5 images
        And I forcefully set the slideshow delay to 50ms
        When I run slideshow
        And I wait for 120ms
        Then the image should have the index 3
