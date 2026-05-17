"""
Scrble - Word Dictionary
Loads 117,000+ English words from a compressed dictionary file at startup.
Words sourced from American + British English dictionaries, proper nouns excluded.
"""
import gzip
import os

_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'words.txt.gz')

def _load():
    try:
        with open(_WORDS_FILE, 'rb') as f:
            data = gzip.decompress(f.read()).decode('utf-8')
        return set(data.split())
    except Exception as e:
        # Fallback: minimal set so the game still runs
        print(f'[Scrble] Warning: could not load dictionary ({e}), using fallback.')
        return set('''
            aa ab ad ae ag ah ai al am an ar as at aw ax ay ba be bi bo by
            da de do ea ed ef eh el em en er es et ex fa fe fi gi go ha he
            hi ho id if in is it jo ka ki la li lo ma me mi mo mu my na ne
            no nu ob od oe of oh oi ok om on op or os ow ox oy pa pe pi po
            qi re sh si so ta te ti to uh um un up us ut we wo xi xu ya ye
            yo za ace act add ado age ago aid aim air ale amp and ant any
            ape apt arc are ark arm art ash ask asp ate atm auk ave awe awl
            awn axe aye bad bag ban bar bat bay bed beg bet bid big bin bit
            boa bob bod bog bon boo bop bot bow box boy bra bub bud bug bun
            bur bus but buy bye cab cad cam can cap car cat caw cel chi cob
            cod cog col con coo cop cor cos cot cow cox coy cub cud cup cur
            cut dab dad dag dam dap day deb dee den dew die dig dim din dip
            dis doc doe dog don dos dot dow dub dud due dug dun duo dye ear
            eat eek eel egg ego eke elf elk ell elm emu end era err eta eve
            ewe eye fad fan far fat fax fay fed fen few fey fez fib fie fig
            fin fit fix fob foe fog fop for fox foy fro fry fun fur gab gad
            gag gal gap gas gay gel gem get gib gig gin gnu gob god goo got
            hag ham hap has hat haw hay hem hep her hew hex hey hid him hip
            his hit hob hod hoe hog hop hot how hoy hub hue hug hum hun hut
            ice icy ilk imp ink inn ins ion ire irk ivy jab jag jam jar jaw
            jay jib jig job jog jot joy jug jus jut keg ken key kid kin kit
            lab lac lad lag lam lap law lax lay lea led leg let leu ley lid
            lip lit lob log loo lop lot low lox lug mac mad man map mar mat
            maw max may med men met mew mid mil mob mod mom moo mop mot mow
            mud mug mum nab nag nap nay neb nee net new nib nil nip nit nix
            nob nod nor not now nun nut oaf oak oar oat odd ode off oft ohm
            oil old ole one opt orb ore our out owe own pad pal pan pap par
            pat paw pay pea pec pee peg pen pep per pet pew phi pie pig pin
            pip pit pix ply pod pol poo pop pot pow pro pry pub pud pug pun
            pup pus put rag ram ran rap rat raw ray reb rec red ref rem rep
            ret rev rex ria rib rid rig rim rip rob rod roe rot row rub rug
            rum run rut rye sab sad sag sap sat saw sax say sea sec see seg
            sen ser set sew sex sha she shy sic sim sin sip sir sit ski sky
            sly sob sod son sop sot sow sox soy spa spy sty sub sue sum sun
            sup tab tad tan tap tar tat taw tax tea teg ten the tip toe ton
            too top tot tow toy try tub tug tun two van var vat veg vet vex
            via vie vim vow wad wag wan war was wat way web wed wee wen wet
            who why wig win wit woe wok won woo wot wow yam yap yaw yea yen
            yet yin yon you zag zap zed zee zig zip zit zoo able acid acre
            acts adds aged ages aloe also alto alum amps ands anew ante ants
            apex apes arch area arks arms army ates atop auks aunt aura auto
            avid avow awed awes awls awry axes axle axon ayes babe back bade
            bags bail bald bale balk ball balm band bane bang bank bans bare
            bark barn bars bash bask bass bate bath bats bawl bays bead beak
            beam bean bear beat been beep beer bees beet bell belt bend bent
            berg best beta bets bias bide bile bill bind bins bite bits blow
            blue blur boar bobs bode body bogs bold bolt bond bone bong bony
            book boom boon boor boot bore born boss both bout bowl boys brag
            bran brat brew brig brow buck buff bugs bulk bull bump bunk buns
            burn burp bury bush busy butt cafe cage cake call calm came camp
            cane cant care carp cart case cash cask cast cave cell cert chap
            chat chef chew chin chip chop chow cite clam clap clay clip clot
            club clue coal coat cobs cock coda code cods coil coin cola cold
            colt come cone cool cope cord core cork corn cost cove cozy crab
            cram crew crib crop crow cube cubs cued cuff cull cult cups curb
            curl curs curt cuss dame damp dare dark darn dart dash date daub
            daze dead deaf deal dean debt deck deed deer deft deny desk dial
            dice dike dime dine ding dink dire dirk dirt disc dish disk diva
            dive dock dome done dorm dote dove down drab drag draw drew drip
            drop drum dual dubs dude duel duet dupe dusk dust each earl earn
            ease edit ells emit envy epic erst even ever exam exec exes expo
            eyed eyes face fact fade fail fair fake fall fame fang fare farm
            fast fate fawn faze fear feat feel feet fell felt fend fern fest
            feta feud file fill film find fine fink fire fish fist five flag
            flat flaw flea flew flex flip flit floe flog flop flow flue flux
            foam foil folk fond font food fool fore fork form fort foul four
            fowl fray free fret frog from fuel full fume fund funk furl fuse
            fuss gads gain gale gall gals game gamy gang garb gash gasp gate
            gave gear geld gene gent germ gild gill gird girl gist give glee
            glob glow glut gobs gods gold gong gore gory gush gust guys hack
            hags hail hair hall halt hand hang hank hard hare hark harm harp
            hart hash hate haul hawk haze heed heel heir held helm help here
            hewn hick hide hike hill hilt hire hoax hock hoed hogs hold hole
            holm holt home hood hoof hook hope horn hose host hour hove howl
            hubs hull hump hunk hunt hurl hurt husk hymn icon idle ills ired
            inch iron isle itch jabs jade jail jamb jape jaws jazz jean jeer
            jell jerk jibs jigs jilt jinx jock join joke jolt josh jots jowl
            joys judo junk jury just kale keen keep kelp kern kick kids kill
            king kink knit knob knot know labs lace lack lade lady lain lake
            lamb lame lamp land lane lard lark lash lass laud lava laze lazy
            lead leaf leak lean leap left lend lens lent levy lick lied lieu
            like lima limp line link lint lion list live load loan lock loft
            loin look loom loon lope lore loud lour lout love lube lull lure
            lurk lush lust lute mace made mail main make male mall malt mane
            mare mark marl mash mast mate math maul maze mead meal mean melt
            mere mesh mild mile mill mime mind mine mink mint mire miss mite
            moat mock mode mole molt moot more moss most mote mule mull musk
            must mutt nabs narc nark nave neck need nerd nest nick nips node
            none norm nose note noun nuke null odds omen omit once orbs orca
            ores oven oval over owed owns pace pack pact page paid pail pain
            pair pale pall palm pane pang park part pass past pave pawn peak
            peal peck peek peen peer pelt pens pest pick pier pile pill pine
            pink pint pipe pith pity plan plea play plow plug plum plus poem
            poet poke poll polo pond pone poor pope pore pork port pour pout
            prom prop prow puck pull pump punk puny purl push quay quid quiz
            race rack raft rage raid rail rain rake ramp rang rank rant rape
            rare rash rasp rate rave read real ream reap reef reel rein rely
            rent rest rice rick ride rift rill rime ring riot rise risk rite
            roam roar rode role roll romp rook room root rope rose rout rove
            ruby rude ruff ruin rule rump rune ruse rush rust sack safe saga
            sage sail sake sale sane sash save scan seal seam sear sect seed
            seep self send serf sewn shed shin ship shop shot show shun shut
            sill silo silt sine sink sire site size skim skip slab slag slap
            slat slaw sled slim slip slit slob sloe slop slot slow slug slum
            slur smog smug snag snap snob snot snub soak soar sock sofa some
            song soon sort soul soup sour span spar spin spit spot spud spun
            spur stab star stem step stew stir stop stub stud sump sung sunk
            surf swap swat sync tack tale talk tall tame tang tarn tart task
            taut teak teal team tear tell tent tern tide tile tilt time tine
            tire toad toga toke told toll tone tong took tool toot tore torn
            toss tote tour town trap tray trek trim trio trip trod true tuba
            tube tuft tump turf turn twig ugly ulna undo unit unto upon urea
            urge vale vamp vane vary vase vast vein vent verb vest veto vial
            vice view vile vine vise vole volt vote wade wail wait wake wale
            walk wall wane ward warn warp wary watt wave wavy weak weal wean
            weed weep weld went west whim whip whiz wick wide wife wile will
            wily wind wine wing wink wire wise wish wisp wolf womb wont word
            wore worm worn writ yank yard yarn yawn yelp yore your yuan yule
            zany zeal zero zest zinc zing zone zoom play tile hello world
            place blast crane trade flag
        '''.split())

# Load once at module import
VALID_WORDS = _load()


def is_valid_word(word: str) -> bool:
    return word.lower().strip() in VALID_WORDS


def get_word_list():
    return VALID_WORDS
