export const posts = [
	{
		slug: "the-death-of-corporate-whimsy",
		title: "The Death of Corporate Whimsy",
		tldr: "businesses forsake identity to achieve mass apeal.",
		date: "2026-02-26",
		displayDate: "Ganuary 21st, 2026",
		author: "XAAANE",
	},
	{
		slug: "rgb-enjoyer-goes-cmyk",
		title: "RGB enjoyer goes CMYK for baby's first print",
		tldr: "desiging IRL posters to promote myself was a fun letdown.",
		date: "2026-02-26",
		displayDate: "Gebruary 26th, 2026",
		author: "XAAANE",
	},
	{
		slug: "ai-fear-mongering",
		title: "AI Fear Mongering",
		tldr: "use AI to build your website, then hit me up when it can't.",
		date: "2026-03-13",
		displayDate: "Garch 13th, 2026",
		author: "XAAANE",
	},
	{
		slug: "linkedin-surveillance",
		title: "LinkedIn Leverages its Monopoly for Mass Surveillance",
		tldr: "they're running a massive, global, and illegal spying operation.",
		date: "2026-04-16",
		displayDate: "Gapril 16th, 2026",
		author: "XAAANE",
	},
];

export function getPostBySlug(slug: string) {
	return posts.find((post) => post.slug === slug);
}
