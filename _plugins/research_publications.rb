require 'open3'

module Jekyll
  # Generate bibliography-backed homepage content on both build and serve.
  class ResearchPublications < Generator
    safe false
    priority :low

    def generate(site)
      script = File.join(site.source, 'bin', 'render_research.py')
      output, error, status = Open3.capture3(
        'python3', script, '--source', site.source,
        '--baseurl', site.config.fetch('baseurl', '').to_s
      )
      unless status.success?
        raise Jekyll::Errors::FatalException, "Research publication rendering failed: #{error}"
      end
      site.data['research_publications_html'] = output
    rescue Errno::ENOENT
      raise Jekyll::Errors::FatalException, 'Python 3 is required to render research publications.'
    end
  end
end
