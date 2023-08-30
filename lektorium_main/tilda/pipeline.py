from openedx_filters import PipelineStep
from openedx_filters.learning.filters import CourseAboutRenderStarted
    
    
class RenderAlternativeCourseAbout(PipelineStep):
    """
    Stop course about render raising RenderCustomResponse exception.

    Example usage:

    Add the following configurations to your configuration file:

        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.course_about.render.started.v1": {
                "fail_silently": False,
                "pipeline": [
                    "openedx_filters_samples.samples.pipeline.RenderAlternativeCourseAbout"
                ]
            }
        }
    """

    def run_filter(self, context, template_name):  # pylint: disable=arguments-differ
        """
        Pipeline step that renders a custom template.

        When raising the exception, this filter uses a redirect_to field handled by
        the course about view that redirects to the URL indicated.
        """
        
        # https://github.com/eduNEXT/platform-plugin-ontask/blob/main/platform_plugin_ontask/extensions/filters.py
        ## TODO: доделать моментик
        raise CourseAboutRenderStarted.RenderInvalidCourseAbout(
            "You can't view this course.",
            course_about_template='static_templates/404.html',
            template_context=context,
        )
