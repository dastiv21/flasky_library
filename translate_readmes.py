from googletrans import Translator, LANGUAGES
import os
import logging

# Set up logging
logging.basicConfig(filename='translation_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary for language-specific technical terms
technical_terms = {
    'en': {
        'function': 'function',
        'variable': 'variable',
        'class': 'class',
        # Add more terms and translations as needed
    },
    'es': {
        'function': 'función',
        'variable': 'variable',
        'class': 'clase',
        # Add more terms and translations as needed
    },
    # Add more languages and their terms here
}


# Function to translate markdown content while preserving markdown formatting
def translate_markdown_content(content, target_language):
    try:
        # Initialize the translator
        translator = Translator()

        # Replace technical terms with language-specific terms
        for term in technical_terms.get('en', {}):
            replacement = technical_terms.get(target_language, {}).get(term,
                                                                       term)
            content = content.replace(term, replacement)

        # Translate the content
        translated_content = translator.translate(content,
                                                  dest=target_language).text
        return translated_content
    except Exception as e:
        logging.error(
            f"Error translating to {LANGUAGES[target_language]}: {e}")
        return None


# Function to translate README files to specified languages with localization
def translate_readmes(readme_files, target_languages):
    for readme_file in readme_files:
        if not os.path.isfile(readme_file):
            logging.warning(f"File {readme_file} does not exist.")
            continue

        try:
            with open(readme_file, 'r', encoding='utf-8') as file:
                original_content = file.read()

            for language in target_languages:
                translated_content = translate_markdown_content(
                    original_content, language)
                if translated_content:
                    output_filename = (f"{os.path.splitext(readme_file)[0]}"
                                       f"_{language}.md")
                    with open(output_filename, 'w', encoding='utf-8') as file:
                        file.write(translated_content)
                    logging.info(
                        f"Translated {readme_file} to {LANGUAGES[language]}"
                        f" and saved as {output_filename}.")
                else:
                    logging.error(
                        f"Failed to translate {readme_file} to"
                        f" {LANGUAGES[language]}.")
        except Exception as e:
            logging.error(f"Failed to translate {readme_file}: {e}")


# Usage
readme_files_to_translate = ['README.md']  # Add more file names as needed
target_languages = ['es', 'fr', 'de', 'yo', 'zh-cn']  # Add more language codes
# as needed
translate_readmes(readme_files_to_translate, target_languages)
