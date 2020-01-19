Feature: Straighten an image.

    Background: 
        Given I open any image

    Scenario: Enter straighten widget
        When I run straighten
        Then there should be 1 straighten widget
        And the center status should include angle: +0.0°

    Scenario: Leave straighten widget discarding changes
        When I run straighten
        And I straighten by 1 degree
        And I leave the straighten widget via <escape>
        Then there should be 0 straighten widgets
        And the image size should be 300x300

    Scenario: Leave straighten widget accepting changes
        When I run straighten
        And I straighten by 1 degree
        And I leave the straighten widget via <return>
        Then there should be 0 straighten widgets
        And the image size should not be 300x300

    Scenario: Straighten image using keybindings
        When I run straighten
        And I hit l on the straighten widget
        Then the straighten angle should be 0.2
