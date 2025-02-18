```
**

olympus/environments/codemonkeys/codemonkeys/prompts/testing_state_machine_prompts.py

  olympus/environments/codemonkeys/codemonkeys/prompts/testing_state_machine_prompts.py:21:102 - error: Type of "version" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/prompts/testing_state_machine_prompts.py:24:2 - error: Type of "problem_statement" is unknown (reportUnknownMemberType)

olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:49:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:49:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:49:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:107:43 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:114:41 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:121:41 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:128:41 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:136:54 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:145:39 - error: Type of "to_dict" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/run_codemonkeys.py:156:3 - error: Argument missing for parameter "config" (reportCallIssue)

olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:27:3 - error: Type of "extract_last_json" is partially unknown

    Type of "extract_last_json" is "(text: Unknown) -> (Any | None)" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:46:3 - error: Type of "file_to_relative_ranks" is partially unknown

    Type of "file_to_relative_ranks" is "dict[str, list[Unknown]]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:50:7 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:54:7 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:58:18 - error: Argument type is partially unknown

    Argument corresponds to parameter "iterable" in function "sum"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:58:31 - error: Argument type is partially unknown

    Argument corresponds to parameter "obj" in function "len"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:80:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:89:10 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:102:24 - error: Type of "problem_statement" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:102:24 - error: Argument type is unknown

    Argument corresponds to parameter "issue_description" in function "user_prompt" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:121:49 - error: Argument of type "list[dict[str, str | list[dict[str, str | dict[str, str]]]]]" cannot be assigned to parameter "messages" of type "Iterable[MessageParam]" in function "create"

    Type "list[dict[str, str | dict[str, str]]]" is not assignable to type "str | Iterable[ContentBlock | TextBlockParam | ImageBlockParam | ToolUseBlockParam | ToolResultBlockParam | DocumentBlockParam]"

      "list[dict[str, str | dict[str, str]]]" is not assignable to "str"

      "list[dict[str, str | dict[str, str]]]" is not assignable to "Iterable[ContentBlock | TextBlockParam | ImageBlockParam | ToolUseBlockParam | ToolResultBlockParam | DocumentBlockParam]"

        Type parameter "_T_co@Iterable" is covariant, but "dict[str, str | dict[str, str]]" is not a subtype of "ContentBlock | TextBlockParam | ImageBlockParam | ToolUseBlockParam | ToolResultBlockParam | DocumentBlockParam"

          Type "dict[str, str | dict[str, str]]" is not assignable to type "ContentBlock | TextBlockParam | ImageBlockParam | ToolUseBlockParam | ToolResultBlockParam | DocumentBlockParam"

            "dict[str, str | dict[str, str]]" is not assignable to "TextBlockParam"

            "dict[str, str | dict[str, str]]" is not assignable to "ImageBlockParam"

            "dict[str, str | dict[str, str]]" is not assignable to "ToolUseBlockParam" (reportArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:134:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:139:18 - error: Argument type is partially unknown

    Argument corresponds to parameter "obj" in function "len"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:140:44 - error: Type of "path" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:162:35 - error: Argument type is unknown

    Argument corresponds to parameter "map" in function "__init__" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:162:46 - error: Type of "usage" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:167:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:167:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/context/ranking.py:167:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:5:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:73:3 - error: Type of "trajectory_store" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:73:22 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:73:22 - error: Type of "get_trajectory_store" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:75:6 - error: Type of "relevance_decision_exists" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:85:53 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:85:53 - error: Type of "max_file_tokens" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:89:11 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:89:11 - error: Type of "model" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:89:11 - error: Argument type is unknown

    Argument corresponds to parameter "model" in function "create" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:92:16 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:92:16 - error: Type of "max_tokens" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:92:16 - error: Argument type is unknown

    Argument corresponds to parameter "max_tokens" in function "create" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:93:13 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:93:13 - error: Type of "timeout" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:93:13 - error: Argument type is unknown

    Argument corresponds to parameter "timeout" in function "create" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:100:3 - error: Type of "save_per_file_relevance_decision" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:116:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:116:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:116:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:129:9 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:140:5 - error: Argument type is partially unknown

    Argument corresponds to parameter "items" in function "parallelize"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/context/relevance.py:147:3 - error: Argument missing for parameter "config" (reportCallIssue)

olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:6:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:185:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:185:15 - error: Type of "container_log_dir" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:186:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:186:15 - error: Type of "exec_timeout" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:211:7 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:211:7 - error: Type of "max_output_chars" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:211:7 - error: Argument type is unknown

    Argument corresponds to parameter "max_chars" in function "render_stdout" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:214:7 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:214:7 - error: Type of "max_output_chars" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:214:7 - error: Argument type is unknown

    Argument corresponds to parameter "max_chars" in function "render_stdout" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:333:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:333:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/editing_state_machine.py:333:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/model_selection.py

  olympus/environments/codemonkeys/codemonkeys/stages/model_selection.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/model_selection.py:97:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/model_selection.py:97:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/model_selection.py:97:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution.py

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution.py:67:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution.py:67:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution.py:67:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py:72:9 - error: Argument type is partially unknown

    Argument corresponds to parameter "cache" in function "run_generated_tests"

    Argument type is "dict[Unknown, Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py:83:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py:83:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_execution_intermediate_edits.py:83:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:78:25 - error: Type of "prompt_caching_usages" is partially unknown

    Type of "prompt_caching_usages" is "list[dict[Unknown, Unknown]]" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:78:25 - error: Argument type is partially unknown

    Argument corresponds to parameter "obj" in function "len"

    Argument type is "list[dict[Unknown, Unknown]]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:82:7 - error: Argument type is partially unknown

    Argument corresponds to parameter "iterable" in function "sum"

    Argument type is "dict_values[str, float] | dict_values[str, Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:84:20 - error: Type of "prompt_caching_usages" is partially unknown

    Type of "prompt_caching_usages" is "list[dict[Unknown, Unknown]]" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:88:15 - error: Type of "prompt_caching_usages" is partially unknown

    Type of "prompt_caching_usages" is "list[dict[Unknown, Unknown]]" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:88:15 - error: Argument type is partially unknown

    Argument corresponds to parameter "obj" in function "len"

    Argument type is "list[dict[Unknown, Unknown]]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:118:7 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:119:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:125:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:130:13 - error: Argument type is partially unknown

    Argument corresponds to parameter "patches" in function "__init__"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:131:11 - error: Argument type is partially unknown

    Argument corresponds to parameter "tests" in function "__init__"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/generated_test_utils.py:132:11 - error: Argument type is partially unknown

    Argument corresponds to parameter "costs" in function "__init__"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:4:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:30:5 - error: Type of "num_samples_per_problem" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:30:36 - error: Type of "REQUIRED" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:30:42 - error: "REQUIRED" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:75:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:75:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation.py:75:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:39:3 - error: Type of "patches" is partially unknown

    Type of "patches" is "set[Unknown]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:42:7 - error: Type of "add" is partially unknown

    Type of "add" is "(element: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:44:48 - error: Argument type is partially unknown

    Argument corresponds to parameter "patches" in function "run_ground_truth_tests_for_patches"

    Argument type is "set[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:49:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:49:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/sample_evaluation/sample_evaluation_intermediate_edits.py:49:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:6:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:141:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:141:15 - error: Type of "container_log_dir" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:142:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:142:15 - error: Type of "exec_timeout" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:169:11 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:169:11 - error: Type of "max_output_chars" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:169:11 - error: Argument type is unknown

    Argument corresponds to parameter "max_output_chars" in function "select_or_revise_prompt" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:217:5 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:231:9 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:233:10 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:239:3 - error: Type of "file_paths" is partially unknown

    Type of "file_paths" is "set[Unknown]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:253:11 - error: Type of "add" is partially unknown

    Type of "add" is "(element: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:254:12 - error: Type of "errors" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:254:12 - error: Type of "UnidiffParseError" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:254:20 - error: "errors" is not a known attribute of module "unidiff" (reportAttributeAccessIssue)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:258:7 - error: Type of "paths" is partially unknown

    Type of "paths" is "list[Unknown]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:259:11 - error: Type of "path" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:260:32 - error: Argument type is unknown

    Argument corresponds to parameter "path" in function "file_exists" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:261:11 - error: Type of "add" is partially unknown

    Type of "add" is "(element: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:261:26 - error: Argument type is unknown

    Argument corresponds to parameter "element" in function "add" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:263:28 - error: Argument type is unknown

    Argument corresponds to parameter "path" in function "get_file" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:263:38 - error: Type of "file" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:286:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:296:10 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:299:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:299:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine.py:299:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:37:5 - error: Type of "leaderboard_names" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:37:30 - error: Type of "REQUIRED" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:37:36 - error: "REQUIRED" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:59:21 - error: Type of "leaderboard_names" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:60:7 - error: Type of "name" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:60:15 - error: Type of "leaderboard_names" is partially unknown

    Type of "leaderboard_names" is "list[Unknown]" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:63:53 - error: Type of "leaderboard_names" is partially unknown

    Type of "leaderboard_names" is "list[Unknown]" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:63:53 - error: Argument type is partially unknown

    Argument corresponds to parameter "names" in function "get_leaderboard_solutions"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:128:5 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:138:10 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:141:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:141:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/selection_state_machine_with_ensembled_solutions.py:141:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:3:8 - error: Stub file not found for "pydra" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:98:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:98:15 - error: Type of "container_log_dir" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:98:15 - error: Argument type is unknown

    Argument corresponds to parameter "log_dir" in function "execute_script" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:99:15 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:99:15 - error: Type of "exec_timeout" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:99:15 - error: Argument type is unknown

    Argument corresponds to parameter "timeout" in function "execute_script" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:134:45 - error: Type of "config" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:134:45 - error: Type of "max_output_chars" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:134:45 - error: Argument type is unknown

    Argument corresponds to parameter "max_chars" in function "render_stdout" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:157:2 - error: Type of "main" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:157:2 - error: Untyped function decorator obscures type of function; ignoring decorator (reportUntypedFunctionDecorator)

  olympus/environments/codemonkeys/codemonkeys/stages/testing_state_machine.py:157:8 - error: "main" is not a known attribute of module "pydra" (reportAttributeAccessIssue)

olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:10:6 - error: Stub file not found for "swebench.harness.docker_build" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:11:6 - error: Stub file not found for "swebench.harness.docker_utils" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:11:43 - error: Type of "cleanup_container" is partially unknown

    Type of "cleanup_container" is "(client: Unknown, container: Unknown, logger: Unknown) -> None" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:32:3 - error: Type of parameter "container" is unknown (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:32:3 - error: Type annotation is missing for parameter "container" (reportMissingParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:33:3 - error: Type of parameter "cmd" is unknown (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:33:3 - error: Type annotation is missing for parameter "cmd" (reportMissingParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:57:7 - error: Type of "exec_id" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:57:17 - error: Type of "client" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:57:17 - error: Type of "api" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:57:17 - error: Type of "exec_create" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:58:9 - error: Type of "id" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:65:9 - error: Type of "exec_stream" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:65:23 - error: Type of "client" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:65:23 - error: Type of "api" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:65:23 - error: Type of "exec_start" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:67:13 - error: Type of "chunk" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:69:13 - error: Type of "exec_result" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:69:28 - error: Type of "decode" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:76:11 - error: Type of "_response" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:76:11 - error: Type of "close" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:92:7 - error: Type of "exec_pid" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:92:18 - error: Type of "client" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:92:18 - error: Type of "api" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:92:18 - error: Type of "exec_inspect" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:93:7 - error: Type of "exec_run" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:100:3 - error: Type of "exit_code" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:100:15 - error: Type of "client" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:100:15 - error: Type of "api" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:100:15 - error: Type of "exec_inspect" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:105:15 - error: Argument type is unknown

    Argument corresponds to parameter "exit_code" in function "__init__" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:146:23 - error: Type of parameter "args" is unknown (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:146:23 - error: Type annotation is missing for parameter "args" (reportMissingParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:148:5 - error: Type of "close" is partially unknown

    Type of "close" is "() -> Unknown" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:162:5 - error: Type of "put_archive" is partially unknown

    Type of "put_archive" is "(path: str, data: Unknown) -> bool" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/containers.py:165:12 - error: Type of "exec_run" is partially unknown

    Type of "exec_run" is "(cmd: Unknown, stdout: bool = True, stderr: bool = True, stdin: bool = False, tty: bool = False, privileged: bool = False, user: str = "", detach: bool = False, stream: bool = False, socket: bool = False, environment: Any | None = None, workdir: Any | None = None, demux: bool = False) -> ExecResult" (reportUnknownMemberType)

olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:5:6 - error: Stub file not found for "swebench.harness.constants" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:11:6 - error: Stub file not found for "swebench.harness.test_spec" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:13:3 - error: Type of "make_env_script_list" is partially unknown

    Type of "make_env_script_list" is "(instance: SWEbenchInstance, specs: dict[Unknown, Unknown], env_name: str) -> list[str]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:14:3 - error: Type of "make_eval_script_list" is partially unknown

    Type of "make_eval_script_list" is "(instance: Unknown, specs: Unknown, env_name: Unknown, repo_directory: Unknown, base_commit: Unknown, test_patch: Unknown) -> (Unknown | list[str])" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:15:3 - error: Type of "make_repo_script_list" is partially unknown

    Type of "make_repo_script_list" is "(specs: Unknown, repo: Unknown, repo_directory: Unknown, base_commit: Unknown, env_name: Unknown) -> list[str]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:31:3 - error: Type of "version" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:31:13 - error: Type of "version" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:34:5 - error: Type of "test_patch" is partially unknown

    Type of "test_patch" is "Unknown | str | None" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:34:18 - error: Type of "gold_test_patch" is unknown (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:38:28 - error: "_row" is protected and used outside of the class in which it is declared (reportPrivateUsage)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:39:25 - error: Argument type is unknown

    Argument corresponds to parameter "s" in function "loads" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:39:34 - error: "_row" is protected and used outside of the class in which it is declared (reportPrivateUsage)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:40:12 - error: Return type is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:40:21 - error: "_row" is protected and used outside of the class in which it is declared (reportPrivateUsage)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:52:51 - error: "_row" is protected and used outside of the class in which it is declared (reportPrivateUsage)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:54:3 - error: Type of "eval_script_list" is partially unknown

    Type of "eval_script_list" is "list[str] | Unknown" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:55:14 - error: "_row" is protected and used outside of the class in which it is declared (reportPrivateUsage)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:69:22 - error: Argument type is partially unknown

    Argument corresponds to parameter "eval_script_list" in function "__init__"

    Argument type is "list[str] | Unknown" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/interface.py:70:13 - error: Argument type is unknown

    Argument corresponds to parameter "version" in function "__init__" (reportUnknownArgumentType)

olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/logging.py

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/logging.py:3:6 - error: Stub file not found for "swebench.harness" (reportMissingTypeStubs)

olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/tst_execution.py

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/tst_execution.py:8:6 - error: Stub file not found for "swebench.harness" (reportMissingTypeStubs)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/tst_execution.py:68:11 - error: Expected type arguments for generic class "dict" (reportMissingTypeArgument)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/tst_execution.py:80:3 - error: Type annotation is missing for parameter "return_error_as_execution_output" (reportMissingParameterType)

  olympus/environments/codemonkeys/codemonkeys/swe_bench/test_runner/tst_execution.py:165:12 - error: Type of "run_instance" is partially unknown

    Type of "run_instance" is "(test_spec: TestSpec, pred: dict[Unknown, Unknown], rm_image: bool, force_rebuild: bool, client: DockerClient, run_id: str, timeout: int | None = None) -> (tuple[str, Any] | tuple[str, dict[str, Any]] | None)" (reportUnknownMemberType)

olympus/environments/codemonkeys/codemonkeys/trajectory_data/store.py

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/store.py:160:12 - error: Return type, "dict[Unknown, Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/store.py:185:7 - error: Type of "append" is partially unknown

    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/store.py:187:12 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:30:3 - error: Type of "prompt_caching_usages" is partially unknown

    Type of "prompt_caching_usages" is "list[dict[Unknown, Unknown]]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:30:31 - error: Expected type arguments for generic class "dict" (reportMissingTypeArgument)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:50:5 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:50:24 - error: Type of parameter "items" is partially unknown

    Parameter type is "list[Unknown]" (reportUnknownParameterType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:50:31 - error: Expected type arguments for generic class "list" (reportMissingTypeArgument)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:50:64 - error: Expected type arguments for generic class "list" (reportMissingTypeArgument)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:51:10 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:53:9 - error: Type of "item" is unknown (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:53:32 - error: Argument type is partially unknown

    Argument corresponds to parameter "iter1" in function "__new__"

    Argument type is "list[Unknown]" (reportUnknownArgumentType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:78:3 - error: Type of "prompt_caching_usages" is partially unknown

    Type of "prompt_caching_usages" is "list[dict[Unknown, Unknown]]" (reportUnknownVariableType)

  olympus/environments/codemonkeys/codemonkeys/trajectory_data/structs.py:78:31 - error: Expected type arguments for generic class "dict" (reportMissingTypeArgument)

  
**
```