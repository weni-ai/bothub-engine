# 6.9.2
## *change*
  - get language now is a method on prompt_formatter and use the language prefix to define the language, default is pt-br
  - in post processing now get the first word and normalize special characters to compare with normalize classes
  - improving the none template text in `en` and `es` languages

# 6.9.1
## *Change*
  - improving the zeroshot prompt

# 6.9.0
## *Add*
  - usecases classes to format prompt and classification

## *Change*
  - zeroshotlog receive options
  - now we send prompts to zeroshot

# 6.8.0
## *Add*
  - Create api repository filters for catergory and repository_type

# 6.7.1
## *Fix*
  - Fixing get filter for existing phrases that need training
  - Fix auto versioning after editing existing phrases

# 6.7.0
# Add
  - zeroshot support to language
# 6.6.0
# Add
  - Token limit validation to content AI

# 6.5.0
# Add
  - Zeroshot elastic docs
  - Zeroshot log data
  - Zeroshot index declared

# 6.4.0
## Add
  - New format to validate flows token on zeroshot

# 6.3.0
## Add
  - New format with singleton to create rabbitmq connection
  - Rabbitmq publisher
  - Integrate AI/project using `ProjectIntelligence` objects
  - When `remove` integration on dash, delete `ProjectIntelligence`
  - Publishing messages when integrate an `AI` with `Project`
  - `integrated_by` field from `ProjectIntelligence`

# 6.2.0
## *Add*
  - Zeroshot flows integration with fast prediction endpoint

# 6.1.0
## *Add*
- Project consumer
- Template type consumer
- Data Transfer Object to project and template type
- Use case to add project creation, template type creation and exceptions

# 6.0.0
## *Add*
  - event driven architecture setup
  - model of template type
  - model of project intelligence
  - parsers
  - eda consumer
  

# 5.8.0
  ## *Add*
    - Field to count the trainings of a repository and `order_by_relevance` method now uses this field

# 5.7.0
  ## *Add*
    - Project model

# 5.6.6
  ## *Fix*
    - translate report

# 5.6.5
  ## *Fix*
    - validation error in RASA imported files now are reported

# 5.6.4

  ## *Fix*
   - entity filter because frontend has not access to entitie.value so used the dict value 'entity'

# 5.6.3

  ## *Add*
    - filter translated example by entity, intent and text value
    - is_trained and original_example_text fields on RepositoryTranslatedExampleSerializer
  
  ## *Change*
    - auto_translation endpoint to receive RepositoryExample id and filter by that to translate examples

# 5.6.2

## *Fix*
  - Update token generator to get user form keycloak with a keycloak rest client

## *Add*
  - adding changelog to project
