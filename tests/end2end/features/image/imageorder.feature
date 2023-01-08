Feature: Ordering the image filelist.

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
