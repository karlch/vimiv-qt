Feature: Mark thumbnails

    Background:
        Given I open 5 images
        And I enter thumbnail mode

    Scenario: Mark a thumbnail
        When I run mark %
        Then the thumbnail number 1 should be marked

    Scenario: Keep correct highlighting when restoring thumbnails
        When I run mark image_03.jpg
        And I run mark image_05.jpg
        And I run delete image_04.jpg
        And I wait for the working directory handler
        And I run undelete image_04.jpg
        And I wait for the working directory handler
        Then the thumbnail number 3 should be marked
        And the thumbnail number 5 should be marked
