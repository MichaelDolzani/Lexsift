# Lexsift - Anki companion for language learning

Lexsift is a fork of [VocabSieve](https://github.com/FreeLanguageTools/vocabsieve) by FreeLanguageTools,
distributed under the GNU GPLv3. See [NOTICE.md](NOTICE.md) for what has changed.

**Coming from VocabSieve?** Lexsift can import your VocabSieve settings, history, tracking data and dictionaries: it offers to on first launch, or use *Import → VocabSieve profile*. See [Moving from VocabSieve](https://michaeldolzani.github.io/Lexsift/installation.html#moving-from-vocabsieve).

## Manual

[Lexsift manual](https://michaeldolzani.github.io/Lexsift/)

## Support

Report bugs and request features on [GitHub Issues](https://github.com/MichaelDolzani/Lexsift/issues).
Please do not take Lexsift-specific problems to the VocabSieve community channels.

Lexsift is a companion program for language learning with Anki. Its primary function is sentence mining, in which sentences with vocabulary words are collected and added into Anki for long term retention. It aims to help intermediate learners gain vocabulary efficiently by allowing card creation with minimal friction. Possible use cases include sentence mining from videos, texts, asynchronously from ereader highlights, and even completely automatically from books or subtitles. See [workflow page](https://michaeldolzani.github.io/Lexsift/workflows) for more details.

## Screenshots

Screenshots are from VocabSieve, from before the fork.

![](docs/assets/demo-0.12.gif)

## Features
- **Quick word lookups and card creation**: Getting definition, pronunciation, and frequency within one or two keypresses/clicks. Only one more click is needed to save the sentence, word, definition and pronunciation as an Anki card.
- **Wide language support**: Supports all languages listed on Google Translate, though it is currently optimized for European languages. Spanish, German, English, and Russian are routinely tested, but all other languages with a similar morphology should work well.
- **Lemmatization**: Automatically remove inflections to enhance dictionary experience (`books` -> `book`, `ran` -> `run`). This works well for most European languages.
- **Local-first**: No internet is required if you use downloaded resources. Lexsift has no central server, so there are no fees to keep it running, so you will never have to pay a subscription.
- **Sane defaults**: Little configuration is needed other than settings for the Anki deck. It comes with two dictionary sources by default for most languages and one pronunciation source that should cover most needs. There is also an included note type, saving you the effort of finding an appropriate one and/or styling it if you don't want to.
- **Local resource support**: Dictionaries in StarDict, Migaku, plain JSON, MDX, Lingvo (.dsl), CSV; frequency lists; and audio libraries. Cognates data can also be imported for more accurate vocabulary tracking.
- **Web reader**: Read epubs with one-click word lookups and Anki export.
- **eReader integration**: Batch-convert [KOReader](https://github.com/koreader/koreader) and Kindle highlights to Anki sentence cards to build vocabulary efficiently without interrupting your reading.
- **Vocabulary tracking**: Track your learning progress effortlessly when you look up (including from ereader), review your Anki cards, or immerse. The data never leaves your computer, and can easily be exported for your own use.
- **Book analysis**: Not sure what to read? Once Lexsift gets enough data of what words you know, it can quickly scan books and predict your level of understanding to help you choose books. 

## Tutorials
[Manual](https://michaeldolzani.github.io/Lexsift/)

[VocabSieve video tutorial](https://www.youtube.com/watch?v=EHW-kBLmuHU) (made for upstream VocabSieve; most of it still applies to Lexsift)

**Windows and Mac users**: If you want to install this program, go to [Releases](https://github.com/MichaelDolzani/Lexsift/releases/) and from the latest release, download the appropriate file for your operating system.

For a nightly build, please check the [CI artifacts page](https://nightly.link/MichaelDolzani/Lexsift/workflows/build-binaries/master). These are not considered ready for release and likely contain bugs. It is recommended to use the debug version to get more details when things go wrong.

## Development
To run from source:
1. Set up a virtual environment `python3 -m venv env`
2. `pip install -r requirements.txt`
3. `python3 lexsift.py`

For debugging purposes, set the environmental variable `LEXSIFT_DEBUG` to any value. This will create a separate profile (settings and databases for records and dictionaries) so you may perform tests without affecting your normal profile. For each different value of `LEXSIFT_DEBUG`, a separate profile is generated. This can be any number or string.

Pull requests are welcome! If you want to implement a significant feature, be sure to first ask by creating an issue so that no effort is wasted on doing the same work twice.

## Status
This is currently beta software. You should not expect it to be completely bug-free, but you may expect that:
- You should not lose data by upgrading to a new release. However, downgrading is not guaranteed to work! When in doubt, back up your data and open an issue before attempting to downgrade.
    - This does not include your settings, which may need to be reset for a new release. This will be indicated on the release notes.
- Using the `master` branch and only upgrading should *usually* not break things, but this is not guaranteed. You are expected to read commit messages to take proper precaution.
    - Using feature branches may break things!

## Feedback
You are welcome to report bugs, suggest features/enhancements, or ask for clarifications by opening a GitHub issue.

## Donations
If you appreciate this tool, consider making a donation to the [Free Software Foundation](https://www.fsf.org/) or the [Electronic Frontier Foundation](https://www.eff.org/) to protect our digital future and defend our freedom. Do your part to refuse to pay for DRM'd content and devices. 

## Credits
Lexsift is based on [VocabSieve](https://github.com/FreeLanguageTools/vocabsieve), © 2022 FreeLanguageTools and contributors.

The definitions provided by the program by default come from English Wiktionary, without which this program would never have been created. [LingvaTranslate](https://github.com/thedaviddelta/lingva-translate) is used to obtain Google Translate results. Fоrvо scraping code is inspired by this [repository](https://github.com/Rascalov/Anki-Simple-Forvo-Audio). Lemmatization capabilities come from [simplemma](https://github.com/adbar/simplemma) and [pymorphy3](https://github.com/kmike/pymorphy3).

App icon is made from icons by Freepik available on Flaticon.
