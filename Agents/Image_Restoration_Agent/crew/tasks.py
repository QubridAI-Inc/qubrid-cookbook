"""
ReVive AI — CrewAI Task definitions for all 6 pipeline stages.
Tasks are assembled here; actual execution is driven by pipeline.py.
"""

from crewai import Task


def build_tasks(agents: dict) -> dict[str, Task]:
    """
    Build and return all 6 tasks referencing the provided agents.

    Args:
        agents: Dict of agent instances from agents.build_agents().

    Returns:
        Dict mapping task names to Task objects.
    """
    task_historian = Task(
        description=(
            "Analyze the uploaded photograph and produce a comprehensive "
            "historical context report. Identify era, photo type, setting, "
            "whether it is black and white, subjects, film type, historical "
            "context, and colorization hints.\n"
            "Image data: {image_base64}\n"
            "Mime type: {mime_type}"
        ),
        expected_output="Valid JSON historical context report",
        agent=agents["historian"],
    )

    task_analyst = Task(
        description=(
            "Examine the photograph for all forms of damage. Use the "
            "historical context from the previous task to inform your "
            "assessment. Produce a comprehensive damage report.\n"
            "Image data: {image_base64}\n"
            "Historical context: {historical_context}"
        ),
        expected_output="Valid JSON damage assessment report",
        agent=agents["analyst"],
        context=[task_historian],
    )

    task_strategist = Task(
        description=(
            "Create a precise restoration brief based on the damage report. "
            "Map each damage type to specific PIL/OpenCV operations with exact "
            "parameters. Determine if colorization is required.\n"
            "Damage report: {damage_report}\n"
            "Historical context: {historical_context}"
        ),
        expected_output="Valid JSON restoration brief with step-by-step operations",
        agent=agents["strategist"],
        context=[task_historian, task_analyst],
    )

    task_restorer = Task(
        description=(
            "Execute the restoration brief step by step using the available "
            "image processing tools. Apply each operation in order.\n"
            "Restoration brief: {restoration_brief}\n"
            "Image path: {image_path}"
        ),
        expected_output="Path to restored image file",
        agent=agents["restorer"],
        context=[task_strategist],
    )

    task_colorizer = Task(
        description=(
            "If the photo is black and white (is_black_and_white=True), create "
            "and apply a historically accurate colorization plan. If color photo, "
            "skip and pass through the restored image path.\n"
            "Historical context: {historical_context}\n"
            "Colorization hints: {colorization_hints}\n"
            "Restoration brief: {restoration_brief}\n"
            "Restored image path: {restored_image_path}"
        ),
        expected_output="Path to colorized image file or original restored path",
        agent=agents["colorizer"],
        context=[task_historian, task_strategist, task_restorer],
    )

    task_inspector = Task(
        description=(
            "Compare the ORIGINAL and FINAL restored/colorized image. "
            "Score the restoration quality from 0-100. "
            "If score < 60, verdict must be NEEDS_RETRY.\n"
            "Original image: {image_base64}\n"
            "Final image: {final_image_base64}"
        ),
        expected_output="Valid JSON QA report with score and verdict",
        agent=agents["inspector"],
        context=[task_historian, task_analyst, task_colorizer],
    )

    return {
        "historian": task_historian,
        "analyst": task_analyst,
        "strategist": task_strategist,
        "restorer": task_restorer,
        "colorizer": task_colorizer,
        "inspector": task_inspector,
    }
