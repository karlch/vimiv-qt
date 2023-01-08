Feature: Ordering the image filelist.

    Scenario: Re-order current filelist
        Given I open 12 images without leading zeros in their name
        # When I run set sort.image_order natural
        Then the image should have the index 01
        And the image number 1 should be image_1.jpg
        And the image number 2 should be image_2.jpg
        And the image number 11 should be image_11.jpg

    Scenario: Reverse current filelist
        Given I open 5 images
        When I run set sort.reverse!
        # We revert the sorting, but keep the selection
        Then the image should have the index 5

    Scenario: Shuffle current filelist
        Given I open 15 images
        When I run set sort.shuffle!
        # We revert the sorting, but keep the selection
        Then the filelist should not be ordered
