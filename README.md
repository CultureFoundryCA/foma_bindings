# foma_bindings: Foma Python Bindings

These are python bindings for `foma`, [a finite-state toolkit](https://fomafst.github.io/) developed by [Dr. Mans Hulden](https://www.colorado.edu/linguistics/mans-hulden). These bindings are a subset of the functionality of `foma`, and are a modification of the file(s) in the `python` folder in the above `foma` repo. Those file(s) are edited, expanded, cleaned up, and packaged for distribution through `pip`; the changes made are listed below. 

For additional functionality, please feel free to open up an issue [on our github page](https://github.com/CultureFoundryCA/foma_bindings) describing what you'd like to see, how this is currently accomplished in `foma`, and the reasons why you would like to see this functionality. Feel free to fork this repo and implement the changes yourself as well, and make a pull request and we'll merge it in.

This package is maintained by [CultureFoundry](https://www.culturefoundrystudios.com/) and created in conjunction with [Dr. Miikka Silfverberg](https://linguistics.ubc.ca/profile/miikka-silfverberg/https://linguistics.ubc.ca/profile/miikka-silfverberg/).

## The Bindings

Here is an example of how to use these bindings:

```python
from foma_bindings.fst import Fst

fst = Fst.load("/path/to/compiled/fst.fomabin")

for tagged_word in fst.apply_up("foxes", flags=Fst.TOKENIZE | Fst.PRINT_FLAGS)
    print(tagged_word)
```

## Acknowledgements

Firstly, we would like to acknowledge the extensive work of [Dr. Mans Hulden](https://www.colorado.edu/linguistics/mans-hulden) on the entire `foma` software suite; that software [can be found here](https://fomafst.github.io/). These python bindings only exist because the software that Dr. Hulden wrote is so robust for language use.

Secondly, we would like to acknowledge the work of [Dr. Miikka Silfverberg](https://linguistics.ubc.ca/profile/miikka-silfverberg/https://linguistics.ubc.ca/profile/miikka-silfverberg/). Dr. Silfverberg has extensive experience and knowledge of `foma`, and has been instrumental not only in CultureFoundry's adoption of it in our language programs, but also in working with us to adapt and expand these python bindings to further `foma`'s usability going forward. We hope he will be here to help us, and thereby the communities we are working with, for a long time to come!

## Changelog

### Changes from the original file as part of the Mans Hulden foma repo:

- extensive readability edits have been made, including splitting classes into separate files, alphabetizing the C API mappings, and extensive renaming of function and variable names
- `get_alphabet` and the aliased `get_sigma` functions have been added
- the multi-tape FST class/section has been entirely commented out for now
- additional printing parameters have been added, such as printing with flags included
- the files have been made ready for distribution on `pip`
- apache copyright notices have been added to all the relevant python files
- add query function
- add function to get the flag diacritics

### 0.1.11
- fix bug where `0` was being given as `0+` in the query function for head tags.

### 0.1.10

- add `query_with_head_tags` function to replace `query` function
- add 2 month deprecation warning for `query` function
