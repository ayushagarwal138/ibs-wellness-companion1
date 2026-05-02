'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Heart, Mail, Phone, MapPin, Github, Twitter, Linkedin, ArrowUpRight, Shield, Award, Send } from 'lucide-react';

interface FooterProps {
  variant?: 'default' | 'minimal';
}


export function Footer({ variant = 'default' }: FooterProps) {
  const currentYear = new Date().getFullYear();
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [error, setError] = useState('');

  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    // Simple email validation
    if (!email.match(/^[^@\s]+@[^@\s]+\.[^@\s]+$/)) {
      setError('Please enter a valid email address.');
      return;
    }
    setIsSubscribed(true);
    setEmail('');
    setTimeout(() => setIsSubscribed(false), 3000);
  };

  const footerLinks = {
    product: [
      { href: '/features', label: 'Features' },
      { href: '/pricing', label: 'Pricing' },
      { href: '/demo', label: 'Demo' },
    ],
    support: [
      { href: '/help', label: 'Help Center' },
      { href: '/contact', label: 'Contact Us' },
      { href: '/faq', label: 'FAQ' },
    ],
    company: [
      { href: '/about', label: 'About Us' },
      { href: '/blog', label: 'Blog' },
      { href: '/careers', label: 'Careers' },
    ],
    legal: [
      { href: '/privacy', label: 'Privacy Policy' },
      { href: '/terms', label: 'Terms of Service' },
      { href: '/accessibility', label: 'Accessibility' },
    ],
  };

  const socialLinks = [
    { href: 'https://github.com', icon: Github, label: 'GitHub' },
    { href: 'https://twitter.com', icon: Twitter, label: 'Twitter' },
    { href: 'https://linkedin.com', icon: Linkedin, label: 'LinkedIn' },
  ];

  const contactInfo = [
    { icon: Mail, text: 'support@ibswellness.com', href: 'mailto:support@ibswellness.com' },
    { icon: Phone, text: '+91 800-009-8311', href: 'tel:+918000098311' },
    { icon: MapPin, text: 'Ghaziabad, Uttar Pradesh, India', href: '#' },
  ];

  const trustSignals = [
    { icon: Shield, text: 'HIPAA Compliant' },
    { icon: Award, text: 'FDA Registered' },
  ];

  if (variant === 'minimal') {
    return (
      <footer className="bg-white border-t border-gray-200 backdrop-blur-sm shadow-inner">
        <div className="container mx-auto px-4 py-6 sm:py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-3 group">
              <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Heart className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
              <span className="text-lg sm:text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent tracking-tight">
                IBS Wellness
              </span>
            </div>
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              {trustSignals.map((signal) => (
                <div key={signal.text} className="flex items-center space-x-1">
                  <signal.icon className="h-3 w-3" />
                  <span>{signal.text}</span>
                </div>
              ))}
            </div>
            <p className="text-xs sm:text-sm text-gray-600 font-medium text-center order-last sm:order-none">
              © {currentYear} IBS Wellness Companion. All rights reserved.
            </p>
            <div className="flex items-center space-x-2">
              {socialLinks.map((social) => (
                <Link
                  key={social.label}
                  href={social.href}
                  className="group relative p-2 sm:p-3 rounded-xl bg-gray-50 border border-gray-200 hover:scale-110 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  aria-label={social.label}
                >
                  <social.icon className="h-4 w-4 sm:h-5 sm:w-5 text-gray-600 group-hover:text-blue-600 transition-colors duration-300" />
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="relative bg-gradient-to-br from-gray-50 to-white border-t border-gray-200 shadow-inner overflow-hidden">
      <div className="absolute inset-0 pointer-events-none opacity-40" aria-hidden="true">
        <svg width="100%" height="100%" className="absolute inset-0" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="footer-bg" cx="50%" cy="0%" r="100%">
              <stop offset="0%" stopColor="#e0e7ff" />
              <stop offset="100%" stopColor="white" />
            </radialGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#footer-bg)" />
        </svg>
      </div>
      <div className="relative container mx-auto px-4 py-14 lg:py-20">
        {/* Newsletter Section */}
        <div className="mb-14 text-center">
          <div className="max-w-2xl mx-auto">
            <h3 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight">Stay Updated on Your Wellness Journey</h3>
            <p className="text-gray-600 mb-7 text-base">Get personalized IBS management tips, nutrition insights, and wellness updates delivered to your inbox.</p>
            <form onSubmit={handleNewsletterSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto items-center">
              <div className="relative w-full flex-1">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base shadow-sm transition-all"
                  required
                  aria-label="Email address"
                  disabled={isSubscribed}
                />
                {error && (
                  <span className="absolute left-0 -bottom-6 text-xs text-red-500 font-medium">{error}</span>
                )}
              </div>
              <button
                type="submit"
                disabled={isSubscribed}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-md"
                aria-label="Subscribe to newsletter"
              >
                <Send className="h-4 w-4" />
                <span>{isSubscribed ? 'Subscribed!' : 'Subscribe'}</span>
              </button>
            </form>
            {isSubscribed && (
              <div className="mt-3 text-green-600 text-sm font-medium flex items-center justify-center gap-2 animate-fade-in">
                <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                Subscribed successfully!
              </div>
            )}
          </div>
        </div>

        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-16">
          {/* Brand Section */}
          <div className="lg:col-span-2 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4 group">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg group-hover:scale-110 transition-transform duration-300">
                  <Heart className="h-7 w-7 text-white" />
                </div>
                <span className="text-2xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent tracking-tight">
                  IBS Wellness
                </span>
              </div>
              <p className="text-gray-600 mb-6 leading-relaxed text-base">
                Empowering individuals with IBS to take control of their digestive health through personalized tracking, evidence-based insights, and supportive community resources.
              </p>
            </div>
            {/* Trust Signals */}
            <div className="flex flex-wrap gap-4 mb-6">
              {trustSignals.map((signal) => (
                <div key={signal.text} className="flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg shadow-sm">
                  <signal.icon className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">{signal.text}</span>
                </div>
              ))}
            </div>
            {/* Contact Information */}
            <div className="space-y-3">
              <h4 className="font-semibold text-gray-900 mb-3">Get in Touch</h4>
              {contactInfo.map((contact) => (
                <a
                  key={contact.text}
                  href={contact.href}
                  className="flex items-center space-x-3 text-gray-600 hover:text-blue-600 transition-colors duration-200 group text-base"
                >
                  <contact.icon className="h-4 w-4 group-hover:scale-110 transition-transform duration-200" />
                  <span>{contact.text}</span>
                </a>
              ))}
            </div>
          </div>
          {/* Links Sections */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-semibold text-gray-900 mb-4 capitalize tracking-wide text-lg">
                {category}
              </h3>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-gray-600 hover:text-blue-600 transition-colors duration-200 text-base focus:outline-none focus:underline"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="mt-14 pt-8 border-t border-gray-200 flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <p className="text-sm text-gray-600">
            © {currentYear} IBS Wellness Companion. All rights reserved.
          </p>
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-4">
              {socialLinks.map((social) => (
                <Link
                  key={social.label}
                  href={social.href}
                  className="group relative p-3 rounded-xl bg-gray-100 hover:bg-blue-50 border border-gray-200 hover:border-blue-200 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  aria-label={social.label}
                >
                  <social.icon className="h-5 w-5 text-gray-600 group-hover:text-blue-600 transition-colors duration-300" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}