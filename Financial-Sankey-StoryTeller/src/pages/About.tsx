import { Github, Linkedin, Mail, Globe } from 'lucide-react';

export default function About() {
  const socialLinks = [
    {
      name: 'GitHub',
      url: 'https://github.com/Ethan-pyjs',
      icon: <Github className="w-6 h-6" />
    },
    {
      name: 'LinkedIn',
      url: 'https://linkedin.com/in/phamethanv',
      icon: <Linkedin className="w-6 h-6" />
    },
    {
      name: 'Email',
      url: 'mailto:phamethanv@gmail.com',
      icon: <Mail className="w-6 h-6" />
    },
    {
      name: 'Portfolio',
      url: 'https://your-portfolio.com',
      icon: <Globe className="w-6 h-6" />
    }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-gray-900 bg-opacity-50 rounded-lg p-6 border border-purple-500 border-opacity-20">
        {/* Header Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-purple-300 mb-4">About Me</h1>
          <div className="flex justify-center space-x-4">
            {socialLinks.map((link) => (
              <a
                key={link.name}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-purple-400 transition-colors duration-200"
                aria-label={link.name}
              >
                {link.icon}
              </a>
            ))}
          </div>
        </div>

        {/* Introduction Section */}
        <div className="prose prose-invert max-w-none mb-8">
          <p className="text-gray-300 text-lg leading-relaxed">
            I am a passionate developer with expertise in financial technology and data visualization.
            My focus is on creating intuitive tools that help users understand complex financial data
            through interactive visualizations and clear storytelling.
          </p>
        </div>

        {/* Skills Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-purple-300 mb-4">Technical Skills</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {['React', 'TypeScript', 'Python', 'Data Visualization', 'Financial Analysis', 'D3.js'].map((skill) => (
              <div
                key={skill}
                className="bg-gray-800 bg-opacity-50 rounded-lg px-4 py-2 text-gray-300 text-center border border-purple-500 border-opacity-20"
              >
                {skill}
              </div>
            ))}
          </div>
        </div>

        {/* Projects Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-purple-300 mb-4">Featured Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
              <h3 className="text-xl font-semibold text-purple-200 mb-2">Financial Sankey Story-Teller</h3>
              <p className="text-gray-300">
                An interactive tool for visualizing financial statements using Sankey diagrams and AI-powered insights.
              </p>
            </div>
            {/* Add more projects as needed */}
          </div>
        </div>

        {/* Contact Section */}
        <div>
          <h2 className="text-2xl font-semibold text-purple-300 mb-4">Get in Touch</h2>
          <p className="text-gray-300">
            I'm always interested in connecting with fellow developers and financial technology enthusiasts.
            Feel free to reach out through any of my social links above or email me directly at{' '}
            <a
              href="mailto:your.email@example.com"
              className="text-purple-400 hover:text-purple-300 transition-colors duration-200"
            >
              phamethanv@gmail.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}