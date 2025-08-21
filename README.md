# SeedSpinner - Password List Generator

SeedSpinner is a powerful and flexible password list generation tool designed for security professionals and researchers. It leverages both systematic mutation techniques and AI-powered brainstorming (via Azure OpenAI) to create comprehensive and contextually relevant wordlists for password strength testing and analysis.

SeedSpinner excels at creating deep, targeted wordlists for password recovery and security auditing. Its core strength is performing exhaustive, combinatorial mutations on a small set of high-probability "seed" words. If you have intelligence on what a password might be based on (e.g., a pet's name, a favorite team, a company project), this tool is designed to find the exact, complex permutation the user created.

**Disclaimer:**
This tool is intended for **educational purposes and authorized security testing only**. Using this tool to attempt unauthorized access to any system or account is illegal and unethical. Always obtain explicit, written permission before using this tool on any system you do not own. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

### Inspiration for this tool came from the TV show Mr. Robot using the [elpscrk](https://github.com/D4Vinci/elpscrk) tool; and is the successor project to my [dissertation](https://github.com/tpazz/Password-Security-Gamification). 

![1749035627916](https://github.com/user-attachments/assets/e9b61934-2133-48b3-9281-560180847671)

## Features

*   **Seed Word Input:** Start with a list of base words relevant to your target.
*   **AI-Powered Brainstorming (Optional):**
    *   Integrates with Azure OpenAI (e.g., GPT models).
    *   Expands your initial seed words with related terms, concepts, nicknames, and common associations.
    *   Provides multiple prompt templates (concise, explanatory, creative) for tailored AI suggestions.
    *   User can review and filter AI-suggested words before they are used for mutation.
*   **Systematic Mutation Engine:**
    *   **Capitalisation:** Generates various capitalization patterns (e.g., `word`, `Word`, `WORD`).
    *   **Leet Speak:** Applies common character substitutions (e.g., `a` to `@` or `4`, `e` to `3`).
    *   **Concatenation:** Combines seed words and their variations in different orders.
    *   **Suffix/Prefix Addition (Affixes):** Appends and prepends common numbers, years, and symbols.
*   **Implicit Combination Logic:** Capitalisation and Leet Speak effects are automatically combined if both mutations are enabled, creating more complex variations.
*   **Controlled Affix Application:** Affixes are applied as a final step to fully formed single-word variations (post-Caps/Leet) and to fully formed concatenated strings.
*   **Interactive TUI (Terminal User Interface):**
    *   Menu-driven interface for easy configuration.
    *   Toggle mutation settings ON/OFF.
    *   Set Azure OpenAI endpoint, API key, model name, and system prompt file.
*   **Wordlist Estimation & Preview:**
    *   Provides an approximate calculation of the potential wordlist size (lines and file size) before generation.
    *   Shows a small preview of ~10-20 sample generated passwords.
    *   Calculates an approximate character entropy for the previewed sample.
*   **Memory-Safe Wordlist Generation**
    *   Memory-Safe Generation: Handles extremely large wordlists without crashing by streaming candidates to a temporary file, avoiding high RAM usage.
    *   Leverages System Utilities: Uses optimized command-line tools (sort, uniq) for efficient, disk-based deduplication and sorting of massive lists.

## Prerequisites

*   Python 3.x
*   If using AI brainstorming (optional):
    *   Your Azure OpenAI Endpoint URL.
    *   Your Azure OpenAI API Key.
    *   The Deployment Name of your model.

## Usage
  
 ```bash
 python tui.py
 ```

Core Logic Flow
---
```mermaid
graph TD
    subgraph "1. Initialization"
        A[Start: User provides Base Words & Config] --> B[Create empty Temp File on disk];
    end

    subgraph "2. Single Word Processing"
        B --> C{For each Base Word};
        C --> D[Generate Core Variations - Caps & Leet Combined];
        D --> E[Store Core Variations for Concatenation];
        E --> F[Apply Final Transformations, e.g. Affixes];
        F --> G((Write Single-Word Variations to Temp File));
        G --> C;
    end

    C -- All Base Words Processed --> H{Concatenation Enabled?};

    subgraph "3. Concatenation Processing"
        H -- Yes --> I{For each ordered pair of Base Words};
        I --> J[Retrieve Core Variations for the pair];
        J --> K[Combine all Component Pairs];
        K --> L[Apply Final Transformations to Combined String];
        L --> M((Write Concatenated Variations to Temp File));
        M --> I;
    end

    I -- All Pairs Processed --> N_Finalize;
    H -- No --> N_Finalize;
    
    subgraph "4. Finalization"
        N_Finalize[Process Temp File];
        N_Finalize --> P[Run 'sort' and 'uniq' on Temp File];
        P --> Q[Save result to Final Wordlist];
        Q --> R[Delete Temp File];
    end

    R --> Z[End];

    %% --- Styling ---
    %% Define a single class for the dark theme
    classDef darkTheme fill:#222,stroke:#FFF,stroke-width:2px,color:#FFF;

    %% Apply the dark theme class to ALL nodes in the diagram
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N_Finalize,P,Q,R,Z darkTheme;
    
```
