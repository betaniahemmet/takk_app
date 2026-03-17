import AppShell from "./AppShell.jsx";
import Card from "./ui/Card.jsx";
import HomeButton from "./ui/HomeButton.jsx";

const sections = [
    {
        title: "Så använder du appen",
        description: "Guide till appens funktioner",
        videoSrc: "/media/intro/intro_takk_app.mp4",
    },
    {
        title: "Om projektet",
        description: "Betaniahemmet och TAKK",
    },
    {
        title: "Introduktion till TAKK",
        description: "Grunderna i tecken som stöd",
    },
];

export default function Introduction() {
    return (
        <AppShell title="Introduktion">
            <Card className="p-5 space-y-6">
                <div className="flex items-center justify-between">
                    <h1 className="text-xl font-semibold">Introduktion till TAKK</h1>
                    <HomeButton />
                </div>

                <div className="space-y-8">
                    {sections.map((section) => (
                        <div key={section.title} className="space-y-3">
                            <div>
                                <h2 className="text-base font-semibold">{section.title}</h2>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    {section.description}
                                </p>
                            </div>
                            {section.videoSrc ? (
                                <video
                                    src={section.videoSrc}
                                    controls
                                    playsInline
                                    preload="metadata"
                                    className="w-full aspect-video rounded-lg bg-black"
                                />
                            ) : (
                                <div className="w-full aspect-video rounded-lg bg-black/10 dark:bg-white/10 flex items-center justify-center">
                                    <span className="text-sm text-gray-400 dark:text-gray-500">
                                        Video kommer snart
                                    </span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </Card>
        </AppShell>
    );
}
