Feature: Zoom thumbnails.

    Background:
        Given I open any image
        And I enter thumbnail mode

    Scenario: Increase thumbnail size.
        When I run zoom in
        Then the thumbnail size should be 256

    Scenario: Decrease thumbnail size.
        When I run zoom out
        Then the thumbnail size should be 64

    Scenario: Try to increase thumbnail size below limit.
        # 256
        When I run zoom in
        # 512
        And I run zoom in
        # 512
        And I run zoom in
        Then the thumbnail size should be 512

    Scenario: Try to decrease thumbnail size below limit.
        # 64
        When I run zoom out
        # 64
        And I run zoom out
        Then the thumbnail size should be 64
