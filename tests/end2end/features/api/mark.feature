Feature: Mark and tag images.

    Scenario: Load all marked images
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run open %m
        Then the filelist should contain 2 images
