# Code Contribution Guidelines

Whenever possible, we like to follow generally accepted clean coding standards.

The following rules are guidelines. There will be exceptions to the rules, and we will take exceptions into consideration on a case-by-case basis.

<i>"Code is clean if it can be understood easily — by everyone on the team. Clean code can be read and enhanced by a developer other than its original author. With understandability comes readability, changeability, extensibility and maintainability." - Robert C. Martin</i>

- Adding new code to a repository should follow generally accepted clean coding principles. Your code should:
  - Be Readable - Easy for future developers to understand and contribute to without you.
  - Be Consistent - Follow existing architecture and general paradigms in the code base. If you do something a certain way, do all similar things in the same way.
  - Avoid Complexity - Contributing to large codebases can cause fragile complexity in a system. Keep it simple. Integrate into the existing code base. Refactor existing code when needed. Follow the boy scout rule (Leave the code cleaner than you found it).
  - Root cause solutions/problems - Do not add code that is a “band-aid” or an ad-hoc solution to the problem. This causes code bloat and instability in a system.
- Use descriptive names for variables, functions, and classes. This makes the code self-documenting and easier to understand without extensive comments.
- Only use comments when needed. You don't need to comment on obvious things. When you follow clean coding practices, a lot of your code will be easy to read without comments. Excessive comments lead to a messy codebase and quickly become outdated.

## Adding new Features or Improvement

- You can add to both the main Piccolo AI application code or the user documentation.
- Before you create a new feature or improvement:
  - Create an `RFC Issue` using the GitHub template.
  - When creating a new RFC, choose the appropriate type: Feature or Improvement.
  - Get community/maintainer approval
  - If you have a larger change, you may consider reaching out directly to the maintainers to get feedback and advice.
- New code must include any relevant documentation updates to the user documentation which can be found in the repository at `/docs`

## Checking Out Code/Branching Strategy

- Checkout the main branch.
- Create a new branch for your code changes from main. All feature request and improvement branches should start with `features/`, while bug fix branches should use `bugs/`.
- Create a pull request to merge back to main.

## Code Formatting

- All Python code must be formatted using the Python Black formatter.
  - See install instructions: <https://pypi.org/project/black/>
  - Documentation:
    - <https://black.readthedocs.io/en/stable/the_black_code_style/index.html>
- Follow the established code-writing standards for Python. See the PEP 8 guidelines at <https://peps.python.org/pep-0008/> Here are some main highlights:
  - Use snake_case for variable, function, and class names.
  - Use spaces over tabs for indentation.
  - Put opening braces on the same line as the function or class declaration.
- All JS and JSX code must be run through ESlint with Prettier formatter.
  - See install instructions: <https://eslint.org/>, <https://prettier.io/>
  - We follow the Airbnb JavaScript Style Guide <https://airbnb.io/javascript/>
  - The ESLint configuration file can be found at `/src/ui/.eslintrc.js`

## Test Coverage

- Follow these general testing principles:
  - Test Scope
  - Naming Conventions
  - Assertions
  - Isolation
  - Coverage
- Python:
  - Unit tests are written using the `pytest` framework and located in the `test` directory within your Python application.
- JS and JSX:
  - Unit tests utilize the `jest` framework.
  - For testing components we use `jest` in conjunction with `@testing-library`.
  - All tests reside in the test directory within your JS/JSX codebase.

## New Dependencies

- Python Libraries: Add newly used Python libraries to `/src/server/requirements.txt`
- JavaScript Libraries: Add newly used JavaScript libraries to the dependencies or devDependencies section of `/src/ui/package.json`

## User Documentation Updates

- User documentation is generated using RST (reStructuredText) format
- User documentation is checked in to the repository at `/docs`
- RST Format Guidelines:
  - File names should be all lowercase and hyphenated to separate words (No underscores)
  - Images/Figures should always be center aligned
    >      :align: center
  - Image/File Paths should be absolute
    >      .. figure:: /analytics-studio/img/analytics-studio-build-model-run-pipeline-button.png
  - Content that is in multiple pages should be shared using <b>::include</b> directives (no copy + paste)
    >     .. include:: /guides/getting-started/building-a-model.rst
    >     :start-after:  build-model-start-marker
    >     :end-before:  build-model-end-marker

## Pull Requests

- Pull requests are always welcome, but if you are working on a large update or changing core functionality, it's required to open a `RFC issue` in GitHub prior to working on code to discuss the change with the community/maintainers.
- Pull requests should follow the single responsibility principle. Each pull request should have a single underlying feature/bug that it is adding or changing. This makes code easier to understand, review, and retain a clean commit history for tracking changes.
- Pull request 'title' should be a one-line summary that summarizes the extent of what is being changed in the request.
- When the pull request is associated with a `GitHub issue` then it should link to the issue.
- Make sure functional and unit tests are all passing on your local machine before submitting a pull request.
- Add new functional and unit tests. All new code must have functional and unit tests to test that code.
- Include test instructions on how to manually test your code.
- If you make changes to the existing functionality of the application, then you must update the corresponding documentation with new steps and screenshots. Make sure to include the link to the corresponding documentation pull request.
- The code will be tested automatically through our continuous integration process. The access to the build and test logs is restricted, but you can ask the committers to provide them for you in case of test failures.

## Process for Reporting Bugs

1. First, try and reproduce your bug! It is difficult for a developer to prioritize bugs if they cannot recreate them. Run through your steps and see if it happens every time. If it doesn’t, then what else could it be?
2. Create an `Bug Issue` using the GitHub template.
3. In your steps to reproduce, make sure to detail every step to recreate the issue and any extra information that might be relevant like computer information, installed software version numbers, etc
4. Be aware that sometimes the difference between a bug and a feature is just the way you word the bug report. Try to avoid creating “bugs” that are actually new features.

What about stuff you can’t recreate?

1. Search for any related topics in the SensiML open-source forums
2. Create a topic in the SensiML open-source forums looking for advice or suggestions

If you still haven’t been able to make progress, you should still create a bug report. Sometimes other developers will be able to pinpoint what is causing the issue. However, bug reports that cannot be reproduced or without enough information may be closed or marked as unreproducible on a case-by-case basis.

If you can’t reproduce the issue, it will be harder for contributing developers to prioritize fixing it. However, if you are a contributing developer, be mindful of not brushing off every “can’t reproduce” ticket. If an issue is happening/reported often for users, then it may be worth looking into.