import { Linkedin } from 'lucide-react';

export default function About() {
  const socialLinks = [
    {
      name: 'LinkedIn',
      url: 'https://linkedin.com/in/phamethanv',
      icon: <Linkedin className="w-6 h-6" />
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
            My name is Ethan, I am a student studying Artificial Intelligence and Robotics. I'm very
            passionate about technology and am a strong believer in lifelong learning. This project
            was my final project for my Finance in AI class. I hope that anyone who comes across this
            project finds it useful and informative. I would suggest that you try out different LLMs and see how they perform.
            I'm using a low parameter model for the initial version of this project. 
            I am always open to feedback and suggestions for improvement.
            Please feel free to reach out to me through my LinkedIn or email.
          </p>
        </div>

        {/* Contact Section */}
        <div>
          <h2 className="text-2xl font-semibold text-purple-300 mb-4">Get in Touch</h2>
          <p className="text-gray-300">
            I'm always interested in connecting with fellow developers and financial technology enthusiasts.
            Feel free to reach out through any of my social links above or email me directly at{' '}
            <a
              href="mailto:phamethanv@gmail.com"
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