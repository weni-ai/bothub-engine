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
