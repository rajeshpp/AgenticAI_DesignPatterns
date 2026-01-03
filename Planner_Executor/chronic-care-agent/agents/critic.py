def critic_review(planner_output, executor_outputs):
    issues = []

    if "stop medication" in planner_output.lower():
        issues.append("Unsafe recommendation: stopping medication")

    for output in executor_outputs:
        if "extreme" in output.lower():
            issues.append("Potentially unsafe lifestyle advice")

    return issues
