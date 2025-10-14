import { Config } from "@docusaurus/types";
import { themes } from "prism-react-renderer";

const config: Config = {
  title: "Discovery Intelligence",
  tagline: "Automation and analytics for modern legal discovery",
  url: "https://example.com",
  baseUrl: "/",
  favicon: "img/favicon.ico",
  organizationName: "discovery",
  projectName: "intelligence",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  i18n: {
    defaultLocale: "en",
    locales: ["en"]
  },
  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.ts")
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css")
        }
      }
    ]
  ],
  themeConfig: {
    colorMode: {
      defaultMode: "dark",
      respectPrefersColorScheme: true
    },
    navbar: {
      title: "Discovery Intelligence",
      items: [
        {
          type: "docSidebar",
          sidebarId: "primary",
          position: "left",
          label: "Docs"
        },
        {
          href: "https://github.com/organization/repo",
          label: "GitHub",
          position: "right"
        }
      ]
    },
    prism: {
      theme: themes.nightOwl,
      darkTheme: themes.nightOwl
    }
  }
};

export default config;
