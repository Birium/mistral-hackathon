/**
 * Loader Configurations
 *
 * Defines step sequences and timing for the Chain of Thought loader.
 * Three jurisdiction configs: Australia, United Kingdom, United States.
 *
 * Each step includes:
 * - icon          : Lucide icon rendered next to the step and in the header while active
 * - label         : short text shown inside the expanded content
 * - description   : optional secondary text below the label
 * - headerText    : text displayed in the collapsible header while this step is active
 * - duration      : time in ms before advancing to the next step
 * - searchResults : optional list of source badges shown under the step
 *
 * Each config includes:
 * - completedIcon : icon shown in the header once the sequence finishes
 */

import {
    BookOpen,
    Brain,
    FileCheck,
    FileText,
    GitBranch,
    Scale,
    Search,
    ShieldCheck,
  } from 'lucide-react';
  import type { LucideIcon } from 'lucide-react';
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Types
  // ─────────────────────────────────────────────────────────────────────────────
  
  export interface LoaderStep {
    icon: LucideIcon;
    label: string;
    description?: string;
    headerText: string;
    duration: number;
    searchResults?: string[];
  }
  
  export interface LoaderConfig {
    label: string;
    steps: LoaderStep[];
    completedHeader: string;
    completedIcon: LucideIcon;
  }
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Config — Australia
  // ─────────────────────────────────────────────────────────────────────────────
  
  export const AUSTRALIA_CONFIG: LoaderConfig = {
    label: 'Australia',
    completedHeader: 'Thought',
    completedIcon: Brain,
    steps: [
      {
        icon: Search,
        label: 'Parsing query',
        description: 'Identifying jurisdiction, legislation type, and key legal concepts.',
        headerText: 'Understanding your question...',
        duration: 1500,
      },
      {
        icon: Scale,
        label: 'Querying Australian case law',
        description: 'Searching judgments from Federal, Supreme, and High Court databases.',
        headerText: 'Searching Australian case law...',
        duration: 3000,
        searchResults: [
          'austlii.edu.au',
          'hca.gov.au',
          'federalcourt.gov.au',
          'supremecourt.qld.gov.au',
        ],
      },
      {
        icon: BookOpen,
        label: 'Retrieving relevant legislation',
        description: 'Locating applicable Acts, regulations, and statutory instruments.',
        headerText: 'Checking legislation...',
        duration: 2000,
        searchResults: [
          'legislation.gov.au',
          'austlii.edu.au/au/legis',
          'comlaw.gov.au',
        ],
      },
      {
        icon: ShieldCheck,
        label: 'Verifying citations and authority',
        description: 'Confirming case citations are valid and have not been overruled.',
        headerText: 'Verifying sources...',
        duration: 2500,
        searchResults: [
          'jade.io',
          'austlii.edu.au',
        ],
      },
      {
        icon: GitBranch,
        label: 'Checking for amendments and updates',
        description: 'Ensuring legislation reflects its current in-force version.',
        headerText: 'Checking for recent updates...',
        duration: 2000,
      },
      {
        icon: FileText,
        label: 'Drafting legal analysis',
        description: 'Synthesising findings into a structured, plain-language response.',
        headerText: 'Writing your answer...',
        duration: 2000,
      },
    ],
  };
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Config — United Kingdom
  // ─────────────────────────────────────────────────────────────────────────────
  
  export const UK_CONFIG: LoaderConfig = {
    label: 'United Kingdom',
    completedHeader: 'Thought',
    completedIcon: Brain,
    steps: [
      {
        icon: Search,
        label: 'Parsing query',
        description: 'Identifying applicable UK jurisdiction and area of law.',
        headerText: 'Understanding your question...',
        duration: 1500,
      },
      {
        icon: Scale,
        label: 'Querying UK case law',
        description: 'Searching judgments from the Supreme Court, Court of Appeal, and High Court.',
        headerText: 'Searching UK case law...',
        duration: 3000,
        searchResults: [
          'bailii.org',
          'judiciary.gov.uk',
          'supremecourt.uk',
          'legislation.gov.uk',
        ],
      },
      {
        icon: BookOpen,
        label: 'Retrieving relevant legislation',
        description: 'Locating applicable Acts of Parliament and statutory instruments.',
        headerText: 'Checking legislation...',
        duration: 2000,
        searchResults: [
          'legislation.gov.uk',
          'parliament.uk',
        ],
      },
      {
        icon: ShieldCheck,
        label: 'Verifying citations and authority',
        description: 'Confirming citations are valid and cross-referencing with ICLR records.',
        headerText: 'Verifying sources...',
        duration: 2500,
        searchResults: [
          'iclr.co.uk',
          'bailii.org',
        ],
      },
      {
        icon: GitBranch,
        label: 'Checking for post-Brexit implications',
        description: 'Flagging retained EU law and any divergence from pre-2021 status.',
        headerText: 'Checking for legislative changes...',
        duration: 2000,
      },
      {
        icon: FileText,
        label: 'Drafting legal analysis',
        description: 'Synthesising findings into a structured, plain-language response.',
        headerText: 'Writing your answer...',
        duration: 2000,
      },
    ],
  };
  
  // ─────────────────────────────────────────────────────────────────────────────
  // Config — United States
  // ─────────────────────────────────────────────────────────────────────────────
  
  export const US_CONFIG: LoaderConfig = {
    label: 'United States',
    completedHeader: 'Thought',
    completedIcon: Brain,
    steps: [
      {
        icon: Search,
        label: 'Parsing query',
        description: 'Identifying applicable federal or state jurisdiction and legal domain.',
        headerText: 'Understanding your question...',
        duration: 1500,
      },
      {
        icon: Scale,
        label: 'Querying US case law',
        description: 'Searching judgments from federal circuit courts and the Supreme Court.',
        headerText: 'Searching US case law...',
        duration: 3000,
        searchResults: [
          'courtlistener.com',
          'supremecourt.gov',
          'law.cornell.edu',
          'justia.com',
        ],
      },
      {
        icon: BookOpen,
        label: 'Retrieving relevant statutes',
        description: 'Locating applicable federal and state statutes and regulations.',
        headerText: 'Checking statutes...',
        duration: 2000,
        searchResults: [
          'uscode.house.gov',
          'congress.gov',
          'regulations.gov',
        ],
      },
      {
        icon: ShieldCheck,
        label: 'Verifying citations and authority',
        description: 'Checking citations against Westlaw and confirming cases are still good law.',
        headerText: 'Verifying sources...',
        duration: 2500,
        searchResults: [
          'courtlistener.com',
          'findlaw.com',
        ],
      },
      {
        icon: GitBranch,
        label: 'Checking for circuit splits',
        description: 'Identifying conflicting rulings across federal circuits that may affect outcome.',
        headerText: 'Checking for circuit conflicts...',
        duration: 2000,
      },
      {
        icon: FileCheck,
        label: 'Drafting legal analysis',
        description: 'Synthesising findings into a structured, plain-language response.',
        headerText: 'Writing your answer...',
        duration: 2000,
      },
    ],
  };
  
  // ─────────────────────────────────────────────────────────────────────────────
  // All Configs — exported as a list for the jurisdiction selector
  // ─────────────────────────────────────────────────────────────────────────────
  
  export const ALL_CONFIGS: LoaderConfig[] = [
    AUSTRALIA_CONFIG,
    UK_CONFIG,
    US_CONFIG,
  ];