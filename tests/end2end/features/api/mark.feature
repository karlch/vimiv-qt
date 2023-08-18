Feature: Mark and tag images.

    Scenario: Mark current path
        Given I open 2 images
        When I run mark %
        Then there should be 1 marked images
        And image_01.jpg should be marked

    Scenario: Mark multiple paths
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        Then there should be 2 marked images
        And image_01.jpg should be marked
        And image_02.jpg should be marked

    Scenario: Open all marked images
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run open %m
        Then the filelist should contain 2 images

    Scenario: Write a tag file
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        Then the tag file test should exist with 2 paths

    Scenario: Append to a tag file
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        And I run mark image_03.jpg
        And I run tag-write test
        Then the tag file test should exist with 3 paths

    Scenario: Load a tag file
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        And I run tag-load test
        Then there should be 2 marked images

    Scenario: Load a tag file with empty line
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        And I insert an empty line into the tag file test
        And I run tag-load test
        Then there should be 2 marked images

    Scenario: Delete a tag file
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        And I run tag-delete test
        Then the tag file test should not exist

    Scenario: Open a tag file
        Given I open 5 images
        When I run mark image_01.jpg image_02.jpg
        And I run tag-write test
        And I run tag-open test
        Then there should be 2 marked images
        And the filelist should contain 2 images

    Scenario: Remove deleted file from mark list
        Given I open 5 images
        When I run mark %
        And I run delete %m
        And I wait for the working directory handler
        Then the file image_01.jpg should not exist
        And image_01.jpg should not be marked

    Scenario: Do not crash on non-existing tag
        Given I start vimiv
        When I run tag-load non-existing
        Then no crash should happen
        And the message
            'tag-load: No tag called 'non-existing''
            should be displayed

    Scenario: Do not crash when reading tag without permission
        Given I start vimiv
        When I create the tag 'new_tag' with permissions '000'
        And I run tag-load new_tag
        Then no crash should happen

    Scenario: Do not crash when deleting non-existing tag
        Given I start vimiv
        When I run tag-delete non-existing
        Then no crash should happen
        And the message
            'tag-delete: No tag called 'non-existing''
            should be displayed

    Scenario: Do not crash when deleting tag without permission
        Given I start vimiv
        When I run tag-write new_tag
        And I remove the delete permissions
        And I run tag-delete new_tag
        Then no crash should happen
