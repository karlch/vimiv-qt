Feature: Transform an image.

    Scenario: Crash when running transform without image
        Given I start vimiv
        When I enter image mode
        And I run rotate
        Then no crash should happen

    Scenario: Rotate landscape image
        Given I open any image of size 300x200
        When I run rotate
        Then the orientation should be portrait

    Scenario: Rotate landscape image twice
        Given I open any image of size 300x200
        When I run 2rotate
        Then the orientation should be landscape

    Scenario: Rotate portrait image three times counter-clockwise
        Given I open any image of size 200x300
        When I run 3rotate --counter-clockwise
        Then the orientation should be landscape

    Scenario: Rescale image
        Given I open any image of size 300x200
        When I run rescale 2
        Then the image size should be 600x400

    Scenario: Rescale image changing the aspect ratio
        Given I open any image of size 300x200
        When I run rescale 2 1
        Then the image size should be 600x200

    Scenario: Resize image
        Given I open any image of size 300x200
        When I run resize 150
        Then the image size should be 150x100

    Scenario: Resize image changing the aspect ratio
        Given I open any image of size 300x200
        When I run resize 150 200
        Then the image size should be 150x200

    Scenario: Undo transformations
        Given I open any image of size 300x200
        When I run resize 150
        And I run undo-transformations
        Then the image size should be 300x200

    Scenario: Do not allow transforming when read_only is active
        Given I open any image of size 300x200
        When I run set read_only true
        And I run rotate
        Then the message
            'rotate: Disabled due to read-only being active'
            should be displayed
        And the orientation should be landscape
