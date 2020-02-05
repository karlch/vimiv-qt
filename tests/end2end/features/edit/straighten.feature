Feature: Straighten an image.

    Background: 
        Given I open any image of size 300x200

    Scenario: Enter straighten widget
        When I run straighten
        Then there should be 1 straighten widget
        And the center status should include angle: +0.0°

    Scenario: Leave straighten widget discarding changes
        When I run straighten
        And I straighten by 1 degree
        And I press '<escape>' in the straighten widget
        Then there should be 0 straighten widgets
        And the image size should be 300x200

    Scenario: Straighten repeatedly
        When I run straighten
        And I straighten by 1 degree
        And I straighten by 1 degree
        Then the straighten angle should be 2.0

    Scenario: Leave straighten widget accepting changes
        When I run straighten
        And I straighten by 1 degree
        And I press '<return>' in the straighten widget
        Then there should be 0 straighten widgets
        And the image size should not be 300x200

    Scenario: Straighten image using keybindings
        When I run straighten
        And I press 'l' in the straighten widget
        Then the straighten angle should be 0.2

    Scenario: Straighten already transformed image
        When I run rotate
        And I run straighten
        And I straighten by 1 degree
        And I straighten by -1 degree
        Then the image size should be 200x300
