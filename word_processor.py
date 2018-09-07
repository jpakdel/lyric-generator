import lyricsorter
import slang_cleaner
import scraper
import boto3
import random
from lyricsorter import get_song_url_list, hasNumbers, remove_paranthases
dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
word_relation_table = dynamodb.Table("WordRelation")
song_table = dynamodb.Table("Song")


def get_word_list():
    raw_words = list(word_table.scan()['Items'])
    word_list = []
    word_dict = {}
    word_dict_unsorted = {}
    # print(raw_words)
    i = 0
    for item in raw_words:
        word_list.append(str(item.get("id")))
        try:
            #scraper.update_table(word_table, str(item.get("id")), "songs", len(item['songs']))
            word_dict_unsorted[str(item.get("id"))] = {"num_occurrences": int(item['num_occurrences']),
                                                        "slang": item['slang']}

        except TypeError:
            word_dict_unsorted[str(item.get("id"))] = {"num_occurrences": int(item['num_occurrences']),
                                                        "slang": item['slang']}
            pass
    word_list = sorted(word_list)

    for item in word_list:
        word_dict[item] = word_dict_unsorted[item]
    return [word_list, word_dict]

def fill_word_dict(x: int, y: int):
    """Uses a song url to look up the lyrics and get all the individual words from them"""
    song_urls = get_song_url_list()
    words = get_word_list()
    word_list = words[0]
    word_dict = words[1]

    while x < y:
        if x > len(song_urls) - 1:
            break
        link = song_urls[x]
        x += 1
        response = song_table.get_item(
            Key={
                'id': link
            }
        )

        item = response['Item']
        lyrics = str(item['lyrics'])
        lyric_list = lyrics.split("\n")

        output_list = []
        print(link)
        for item in lyric_list:
            # Take  out the punctuation
            item = item.replace("?", "")
            item = item.replace(",", "")
            item = item.replace(".", " ")
            item = item.replace("\"", "")
            item = item.replace("-", " ")
            item = item.replace("!", "")
            item = item.lower()

            # We only want the line if it doesn't have numbers, and doesn't have a colon, which means its not actual lyrics
            if item not in output_list and hasNumbers(item) is False and scraper.contains(item, ":") is False:
                output_list.append(remove_paranthases(item).strip())

        for item in output_list:
            word_lines = item.split(" ")
            # we only want sentences with more than three words, because some of the text in the lyrics aren'tactual song lyrics
            # and we want to avoid adding those
            if len(word_lines) > 3:
                for word in word_lines:
                    word = str(word).lower()

                    # make sure we aren't adding html code
                    if len(word) > 0 and scraper.contains(word, "&") is False:
                        if word[0] == '\'':
                            word = word[1:len(word)]

                        # replace slang words with their real equivalent\
                        word = slang_cleaner.remove_weirdness(word)
                        slang_word = slang_cleaner.clean_misspellings(word)
                        word = slang_cleaner.clean_slang(slang_word)
                        if word in word_list:
                            num_occurrences = int(word_dict[word]["num_occurrences"]) + 1
                            word_dict[word]["num_occurrences"] = num_occurrences
                            if link not in word_dict[word]["songs"]:
                                word_dict[word]["songs"].append(link)
                            if word != slang_word and slang_word not in word_dict[word]["slang"]:
                                word_dict[word]["slang"].append(slang_word)
    for word in word_list:
        print(word)
        scraper.update_table(word_table, word, "num_occurrences", int(word_dict[word]["num_occurrences"]))
        scraper.update_table(word_table, word, "slang", word_dict[word]["slang"])


def setup_word_table():
    """Initializes the number of occurrences, songs words are found in, and slang deriviatives of all the words in the
    dyanmodb word table"""
    words = get_word_list()
    word_list = words[0]
    for word in word_list:
        print(word)
        scraper.update_table(word_table, word, "num_occurrences", 0 )
        scraper.update_table(word_table, word, "slang", [])
        scraper.update_table(word_table, word, "songs", [])

def reformat_word_table():
    """removes song attribute from all the words"""
    raw_words = list(word_table.scan()['Items'])

    for word in raw_words:
        Item = {'id': word['id'], 'num_occurrences': word['num_occurrences'], 'slang': word['slang']}
        word_table.put_item(
            Item=Item
        )
        print(Item)


def find_nonviable_words():
    response = get_word_list()
    word_list = response[0]
    word_dict = response[1]
    nonviableset = []
    non_viable_words = 0

    numa = 0
    for word in word_list:
        # print(word)
        # print(word_dict['songs'])
        # print(word_dict[word]['num_occurrences'])
        if  word_dict[word]['num_occurrences'] > 1:
            pass
        else:
            non_viable_words+=1
            nonviableset.append(word)



    return(nonviableset)

def find_viable_words():
    response = get_word_list()
    word_list = response[0]
    word_dict = response[1]
    viableset = []
    viable_words = 0

    numa = 0
    for word in word_list:
        # print(word)
        # print(word_dict['songs'])
        # print(word_dict[word]['num_occurrences'])
        if  word_dict[word]['num_occurrences'] > 1:
            viable_words += 1
            viableset.append(word)
        else:
            pass
    return(viableset)


def find_word(words):
    song_urls = get_song_url_list()
    for link in song_urls:
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for line in lyrics:
            for w in line:
                for word in words:
                    if word == w:
                        print(word)
                        print(link)
                        print(line)



# find_word("")
nonviable_words = [
"a's", 'a/c', 'ab', 'abc', 'abel', 'ability', 'aboard', 'abortion', 'absolutely', 'abused', 'abusing', 'academy', 'accepting', 'according',
'accused', 'aces', 'ache', 'achieve', 'achievement', 'aching','acknowledgment', 'acquired', 'acquitted', 'acrobats', 'acted', 'activist',
'adam', 'adapted', 'added','addiction', 'addictions', 'addressing', 'adjust', 'administer', 'admiring', 'adore', 'adrien', 'adventurous',
'adversity', 'advice', 'advil', 'advise', 'aerosol', 'affected', 'africano', 'afros', 'afternoon', 'aga', 'ages','aggravated', 'agitated',
'agreement', 'aids', 'airborne', 'aire', 'aired', 'aires', 'airing', 'airline', 'airport','airports', 'airtight', 'aisle', 'ajar', 'akmaui',
'aladdin', 'alakazam', 'alarms', 'alcoholic', 'alicia', 'alienated','aliens', 'alignment', 'alkaline', 'allah', 'allegations', 'allergies',
'alliance', 'alligators', 'ally','aloe', 'alphabet', 'altoid', 'ama', 'amateurs', 'amaze', 'amazed', 'amazon', 'ambassador', 'amber',
"ambition's",'amethyst', 'amex', 'amigos', 'ammo', 'ammunition', 'amnesia', 'amoeba', 'amongst', 'amounts', 'amphibians', 'anacondas',
'analogist', 'andale', 'aner', 'angelina', 'angliana', 'angry', 'animal', 'animated', 'aniston', 'ankle', 'announcements','anorexic',
'answering', 'ant', 'antennas', 'anti', 'antidote', 'antique', 'ants', 'antsy', 'anxious', 'anyday', 'apen','apeshit', 'apocalypse',
'apology', 'app', 'apparently', 'apply', 'appointment', 'appointments', 'appraisal', 'approaches','approaching', 'appropriate',
'approving', 'appétit', 'apricot', 'apron', 'aquanaut', 'ar', 'arabia', 'arabian', 'arc','arching', 'archive', "aren't",
'argument', 'arkansas', "arm's", 'armor', 'armored', 'arnold', 'aroma', 'arrangement', 'arrest', 'arresting', 'arrival',
'arrived', 'arrows', 'arthritis', 'articles', 'aruba', 'ashanti', 'ashley', 'ashton', 'asics', 'asks', 'asparagus','aspiring',
'assassinating', 'asses', 'assholes', 'assist', 'assists', 'associates', 'assume', 'assumption', 'atf', 'athens', 'athletic',
'attachment', 'attempt', 'attendant', 'attitudes', 'attract', 'attractive', 'auction', 'augusta', 'aunty', 'australian', 'author',
'autistic', 'autobiographical', 'autograph', 'autographing', 'automobiles', 'available', 'avalanche', 'aventador', 'aventadors',
'avion', 'await', 'awkward', 'awol', 'babylon', 'babys', 'bach', "back's", 'backboard', 'backburner', 'backdoor', 'backdoored',
'backfired', 'backpage', 'backs', 'backside', 'backstabbed', 'backstabbing', 'backstage', 'backstreets', 'backup', 'baddie',
'baddies', 'baden', 'bads', 'bagged', 'bagging', 'baggy', 'baguette', 'bahamas', 'bailed', 'baked', 'baker', 'balboa', 'balenci',
'ballad', 'ballenciaga', 'ballerific', 'ballers', 'ballet', 'bama', 'ban', 'bananana', 'bandage', 'bandana', 'bandanna', 'bandannas',
'bandies', 'bandwagon', 'bangladesh', 'bangle', 'bankhead', 'banking', 'banquet', 'banquets', 'banshee', 'baptized', 'barbados',
'barbara', 'barbecue', 'barber', 'barbershop', 'barbwire', 'barclays', 'barfed', 'barker', 'barkley', 'barrack', 'barracuda',
'barred', 'barricades', 'barrier', 'bartending', 'baseball', 'based', 'bashing', 'basket', 'basquiat', 'batch', 'batching',
'bathed', 'bathhouse', 'bathrobes', 'bathrooms', 'batmobile', 'battery', 'battlefield', 'battles', 'bayou', 'bazookas', 'bbq',
'bead', 'beads', 'beanie', 'beavis', 'bebop', 'bedsheets', 'bedspread', 'bedtime', "bee's", 'beehive', 'beeper', 'beers', 'beetle',
'beging', 'begun', 'behave', 'behavior', 'beings', 'believed', 'believing', 'belongs', 'beloved', 'belts', 'beluga', 'benadryl',
'bends', 'benefit', 'benihana', 'benny', 'benzes', 'berettas', 'berg', 'berlin', 'bernard', 'betray', 'betting', 'bezzel',
'bg', 'bi', 'biased', 'biatrice', 'bibles', 'bickering', 'bicoastal', 'bicurious', 'bicycle', 'biddy', 'bifocal', 'biggies',
'billboard', 'billionaire', 'billionaires', 'billions', 'bin', 'binoculars', 'bionic', 'biracial', "bird's", 'birdplay',
'birkins', 'birth', 'biscuit', 'bisexual', 'bishop', 'bitched', 'bitching', 'bites', 'bizzy', 'bk', 'blackberry', 'blackened',
'blackjack', 'blackson', 'bladder', 'blade', 'blake', 'blam', 'blanco', 'blasts', 'blazer', 'blazing', 'bleached', 'bleak', 'bleeds',
'blend', 'blicky', "blimp's", 'blinders', 'blindfold', 'blister', 'bloc', "block's", 'blockbuster', 'blocked', 'blog', 'blondes',
'blooded', 'bloodline', 'blossom', 'blower', 'blows', 'blueprint', 'bluer', 'bluetooth', 'bluff', 'blunted', 'blur', 'blurred',
'blurry', 'blush', 'bmx', 'boarding', "boat's", 'boatload', 'bob', 'bobo', 'bodago', "body's", 'bodybuilder', 'bola', 'bollywood',
'bolt', 'bolted', 'bonded', 'bonding', 'boned', 'boner', 'bonita', 'bonjour', 'bonkers', 'boobies', 'boogie', 'boogieman', 'booked',
'booker', 'bookie', 'bookworm', 'boosted', 'boosters', 'booties', 'bootstrap', 'boozed', 'boozy', 'bops', 'bore', 'borough', 'bot',
'bothered', 'bothering', 'bounced', 'bouncer', 'bouncers', 'bound', 'bountiful', 'bounty', 'bourse', "bowel's", 'bowls', "boy's",
'bozos', 'brad', 'brady', 'braiding', 'brainstorming', 'braise', 'brats', 'brax', 'braxton', 'breakdowns', 'breathes', 'bred',
'bribed', 'bricked', 'briefs', 'brightlens', 'brings', "brink's", 'bronco', 'brothel', 'browser', 'bruins', 'bruise', 'bruised',
'bruising', 'brunch', 'brunette', 'brung', 'brushing', 'bs', 'bubbly', 'bud', 'budged', 'budget', 'buds', 'budweiser', 'buffalos',
'buffet', 'buggers', 'builder', 'bullpen', 'bumblebee', 'bumped', 'bumps', 'bums', 'bunions', 'bunk', 'buns', 'burdens', 'burger', 'burgers',
'burglary', 'burners', 'burping', 'burrito', 'buses', 'bush', 'bustdown', 'busted', 'busters', 'butcher', 'butted', 'butthead', 'buzzing',
"by's", "c'mon", "c's", 'cabing', 'cabo', 'caddy', 'cadillac', 'cadillacs', 'caesar', 'cages', 'cain', 'cajun', 'cakes', 'cal', 'calabasas',
'calamari', 'calculus', 'caller', 'calming', 'calving', 'cam', 'camacho', 'cambridge', 'camel', 'camels', 'camp', 'campaign', 'campos',
'canada', 'canadian', 'canal', 'cancelled', 'candies', 'cannibal', 'capers', 'capo', 'capsules', 'caption', 'capture', 'captured', "car's", 'carat', 'carcass', 'careless', 'cargos', 'carlito', 'carnivals', 'carpool', 'carriage', 'carrot', 'cart', 'carte', 'cartels', 'cartridge', 'cashed', 'cashing', 'casinos', 'cask', 'casper', 'cassidy', 'cassius', 'casted', 'casting', 'castles', 'catalog', 'catalogue', 'catapult', 'caterer', 'caterpillar', 'caters', 'catfishing', 'cathedral', 'catholic', 'cattle', 'caucasian', 'caucasians', 'caucus', 'caused', 'causing', 'cavalier', 'caving', 'cavities', 'cavity', 'cavs', 'cayenne', 'caymen', 'celebrated', 'cello', 'cells', 'cellular', 'cellulite', 'celtic', 'centre', 'cerebellum', 'cerebral', 'certainly', 'cesarean', 'chained', 'chaingang', 'chainsaw', 'challenges', 'chancing', 'changes', 'channels', 'chapstick', 'charcoal', 'charged', 'chargers', 'charging', 'chariot', 'charisma', 'charity', "charm's", 'charming', 'chased', 'chattahoochee', 'chatter', "check's", 'checked', 'checklist', 'checkmate', 'checkout', 'cheerleader', 'cheerleading', 'cheesecake', 'chemicals', 'chemist', 'cherokee', 'chete', 'chevys', 'chewed', 'chewing', 'chewy', 'chia', 'childish', 'chilly', 'chimp', 'chimpanzee', 'china', 'chinese', 'chinky', 'chipotle', 'chiquita', 'chiropractor', 'chirp', 'cho', 'chock', 'choked', 'chokehold', 'chooser', 'choosy', 'chopsticks', 'chorus', 'christians', 'christopher', 'chug', 'chunk', 'chute', 'cig', 'cigar', 'cigarette', 'cinemax', 'cinnabon', 'cinnamon', 'circus', 'cities', 'citizens', 'civics', 'civil', 'civilian', 'civilians', 'claims', 'clams', 'clang', 'clashing', 'classmates', 'clay', 'cleaned', 'cleanest', 'cleans', 'cleared', 'clearing', 'cleavage', 'cleaver', 'climax', 'clinking', 'clippers', 'clipping', "clique's", 'clitoris', 'clocking', 'cloning', 'closes', 'closure', 'clot', 'cloth', 'clothing', 'cloths', 'clotting', 'cloudy', 'clouted', 'clovers', 'clubs', 'clueless', 'clues', 'clumps', 'clumsy', 'coaches', 'coastal', 'coasters', 'coated', 'coating', 'coats', 'cochran', 'cockroaches', 'cocksuckers', 'cocktails', 'coconut', 'cody', 'coined', 'coins', 'colada', 'colbert', 'coldhearted', 'cole', 'colgate', 'collared', 'collections', 'collide', 'collision', 'colombine', 'colon', 'colorblind', 'colossal', 'colour', 'colts', 'columbus', 'coma', 'comatose', 'combination', 'combine', 'combs', 'comma', 'commands', 'commenting', 'comments', 'commercials', 'commissary', 'commissioner', 'committee', 'committing', 'commodity', 'communist', 'community', 'companies', 'comparison', 'comparisons', 'compete', 'complimentary', 'comprehend', 'compressor', 'compromising', 'compton', 'computed', 'computers', 'conceded', 'conceited', 'concentrating', 'concentration', 'concords', 'condos', 'cone', 'conference', 'confessions', 'confident', 'confined', 'confrontation', 'confrontations', 'confuse', 'confusion', 'conga', 'conman', 'connecting', 'conniving', 'conquer', 'cons', 'consider', 'consistent', 'consistently', 'constantly', 'constipated', 'contact', 'contagious', 'continent', 'continue', 'contort', 'contract', 'contractions', 'contractor', 'contribution', 'controlled', 'controversy', 'conversate', 'conversating', 'conversing', 'convertible', 'convicted', 'convicts', 'convince', 'coochies', 'cookout', 'coolant', 'coolie', 'coop', 'cooper', 'copacetic', 'copier', 'copycats', 'copying', 'coral', 'cordial', 'corella', 'cork', 'corpse', 'correctly', 'corridor', 'cosign', 'cosmos', 'costing', 'counseling', 'countries', 'countrywide', 'coup', 'coupons', 'coups', 'courthouse', 'courts', 'couture', 'cowabunga', 'cowboys', 'cowgirl', 'coyote', 'cozy', 'cpr', 'crab', 'crabs', 'cracker', 'cracks', 'cradles', 'cramp', 'cramped', 'cranberry', 'craps', 'craters', 'crave', 'craving', 'crayon', 'creamed', 'creams', 'credentials', 'creed', 'crickets', 'cristal', 'critic', 'crocodile', 'crook', 'crop', 'crossing', 'crossover', 'crossroads', 'crouch', 'crowbar', 'crucifix', 'cruel', 'crunching', 'crushes', 'cs', 'cuatro', 'cubaner', 'cubicle', 'cuckoo', 'cuddling', 'cuffed', 'cuffer', 'cuffs', 'cuisine', 'culos', 'cums', 'cupboard', 'cupid', 'cupping', 'cure', 'curious', 'curly', 'current', 'curses', 'curtis', 'curved', 'curvy', 'cuss', 'custody', 'custom', 'cuticles', 'cutlas', 'cutler', 'cuz', 'cycle', 'cyphers', 'cοngratulatiοns', 'cοst', "cοuldn't", 'da', 'dabbed', 'daddys', 'dahmer', 'dam', 'damage', 'damages', 'dame', 'dames', 'damian', 'damned', 'dane', 'daniel', 'danny', 'darkest', 'darts', 'dashing', 'database', 'dated', 'davis', 'daycare', 'daydreaming', 'daylight', 'deacon', 'deadbolt', 'deadly', 'deads', 'debate', 'debating', 'debutante', 'decapitate', 'deceive', 'december', 'decent', 'decide', 'decimals', 'declare', 'decor', 'decoration', 'decoys', 'dedicate', 'deebowing', 'deepest', 'deers', 'deface', 'defeated', 'defective', 'defend', 'defending', 'definite', 'dehydrated', 'delaying', 'delicate', 'delicious', 'delirious', 'demand', 'demanded', 'demanding', 'demo', 'democracy', 'democrat', 'democratic', 'demonic', 'demonstrating', 'den', 'deng', 'denial', 'denmark', 'dent', 'dental', 'dentures', 'denying', 'department', 'deploy', 'deposits', 'depot', 'depressed', 'des', 'describe', 'designed', 'desire', 'desires', 'despise', 'dessert', 'desserts', 'destroy', 'destroyed', 'detail', 'detectives', 'detonate', 'detrimental', 'detroit', 'dew', 'dhabi', 'diablo', 'diabolical', 'diagnosed', 'dialling', 'dials', 'diam', 'diced', 'dices', 'dicking', 'didi', 'diet', 'digest', 'digiorno', 'dignity', 'dikes', 'dildo', 'dill', "dillard's", 'dimed', 'diminish', 'din', 'dinero', 'dining', 'dipset', 'direct', "director's", 'disagree', 'disclose', 'disclosure', 'discontinued', 'discounts', 'discovered', 'discrete', 'discretion', 'disect', 'disgust', 'dishing', 'dismantle', 'dismiss', 'dismissal', 'dismissed', "disneyland's", 'disobey', 'disowned', 'dispatch', 'dispersed', 'disposal', 'disregard', 'distance', 'distinguished', 'distracted', 'distraction', 'district', 'dita', 'ditch', 'dived', 'diverse', 'diversity', 'divide', 'dividends', 'divorce', 'divorced', 'dixie', 'dixon', 'doc', 'dodged', 'doer', 'doll', 'dolly', 'domain', 'dominate', 'dominatrix', 'dominican', 'domino', 'donatella', 'donkeys', 'doobie', 'dookie', 'dooley', 'doorbell', 'doped', 'dos', 'dosed', 'doses', 'dots', 'doubled', 'doubletree', 'dousing', 'dover', 'doves', 'downfall', 'downgraded', 'dracos', 'dragged', 'dragons', 'drawls', 'drawn', 'dread', 'dreaded', 'dreadlock', 'drenched', 'drexter', 'dribble', 'drier', 'drifting', 'drilled', 'drinker', "driver's", 'drives', 'driz', 'drones', 'drool', 'droppers', 'drums', 'dryer', 'duce', 'duckys', 'duct', 'duffled', 'duffles', 'dug', 'duke', 'dukes', 'duller', 'dummies', 'dumpster', 'dundee', 'dungarees', 'dunks', 'dunno', 'duracell', 'during', 'dusting', 'dusty', 'dutch', 'dwarves', 'dweller', 'dyed', 'dylan', 'dynasty', 'dysfunction', 'dysfunctional', 'dοuble', "e's", 'eardrums', 'earl', 'earmuffs', 'earthquake', 'easier', 'eastside', 'eater', 'eats', 'eavesdropping', 'ebola', 'ec', 'echelon', 'echo', 'economy', 'ecstacy', 'edged', 'edward', 'ee', 'eel', 'eeny', 'effect', 'effervescent', 'effing', 'effort', 'effortlessly', 'egotistic', 'eiffel', 'eighties', 'eigth', 'einstein', 'elaborate', 'elated', 'elbow', 'elbowed', 'elders', 'election', 'electric', 'elements', 'elephants', 'eleventh', 'eliante', 'eliott', 'elliantte', 'elliott', 'elmer', 'email', 'embalming', 'embarrass', 'embarrassing', 'embassy', 'embedded', 'embracing', 'emeralds', 'emmy', 'emoji', 'empathy', 'emperor', 'emphasis', 'employ', 'employed', 'empowerment', 'ems', 'en', 'encourage', "end's", 'energies', 'energized', 'enforced', 'enforcers', 'enforcing', 'engagement', 'enslavement', 'entertain', 'entertainment', 'enticing', 'entire', 'entrance', 'entrepreneur', 'envied', 'environment', 'epi', 'epic', 'equipped', 'erasable', 'eres', 'err', 'erving', 'ese', 'eses', 'espanol', 'espy', 'esquire', 'essentials', 'establishing', 'estate', 'esteem', 'esther', 'estrogen', 'eternity', 'etiquette', 'eulogies', 'euphoria', 'euro', 'european', 'evaporate', 'eve', 'everlasting', 'everynight', 'evicted', 'evicting', 'evident', 'exaggerate', 'exaggeration', 'exam', 'example', 'excellent', 'exchanged', 'excluding', 'exclusively', 'excursion', 'executing', 'executives', 'exhausting', 'existed', 'existence', 'exoskeleton', 'expand', 'expanded', 'expect', 'expected', 'expiring', 'explanatory', 'explosion', 'expo', 'exposure', 'exposured', 'express', 'extortion', 'extreme', 'extremes', 'eyeballs', 'eyed', 'eyeing', 'eyelids', 'fab', 'fabric', 'fabrics', 'faced', 'facelifts', 'facial', 'facials', 'facing', 'faction', 'factories', 'factory', 'fadeaway', 'failing', 'fainting', 'fakers', 'fakery', "falcon's", 'fallen', 'fallon', 'falls', 'false', 'familiar', 'fangs', 'fanny', 'fantasia', 'fargo', 'farmer', 'farmers', 'farms', 'fart', 'farther', 'fasting', 'fates', 'fattest', 'favourite', 'fbi', 'feasting', 'feathers', 'feature', 'featured', 'febreeze', "fed's", 'federales', 'feedback', 'feeds', "feeling's", 'fellatio', 'fellows', 'feminine', 'fend', 'fendis', 'feral', 'ferocious', 'fetch', 'fiat', 'fiber', 'fidget', 'fifths', 'fillings', 'filter', 'finals', 'finders', 'finer', 'finessed', 'finisher', 'finneran', 'firearm', 'firefighter', 'fireman', 'fireplace', 'firework', 'firkins', 'firm', 'fisher', 'fisherman', 'fishing', 'fishtailing', 'fishy', 'fisticuffs', 'fists', 'fits', 'fives', 'flagging', 'flags', 'flake', 'flamboyant', 'flamed', 'flaming', 'flanker', 'flashlight', 'flashy', 'flatline', 'flattering', 'flaw', "flea's", 'fleas', 'fleece', 'flees', 'fleming', 'flesh', 'fletcher', 'flexer', 'flexible', 'flicker', 'flicking', 'flinching', 'flintstone', 'flipper', 'flooding', 'flooring', 'flopping', 'floral', 'florida', 'florist', 'flosser', 'flounder', 'flour', "flower's", 'fluent', 'fluffy', 'flunking', 'flushed', 'flute', 'flyest', "flying's", "fo's", 'foam', 'foes', 'foil', 'folded', 'foldgers', 'folding', "folger's", 'folk', 'followers', 'following', 'follows', 'folly', 'fond', 'fooled', 'foolery', 'foolish', "foot's", 'footage', 'footprint', 'forces', 'forcing', 'fords', 'forecast', 'foreplay', 'forgetting', 'forgiato', 'forgiatos', 'forgies', 'forgiver', 'forgotten', 'forklift', 'form', 'formal', 'formed', 'fornicating', 'forsake', 'forte', 'fortunate', 'fought', 'fouls', 'foundation', 'fourteen', 'fr', 'fraction', 'fractured', 'framed', 'frantic', 'fraternize', 'fraud', 'frauds', 'freakazoid', 'freebie', 'freeing', 'frees', 'freight', 'frenzy', 'freshener', 'freshman', "friend's", "friends'll", 'friendship', 'fright', 'frigid', 'frigidaire', 'frisk', 'frito', 'frogs', 'fronts', 'frostbit', 'frostbite', 'frosty', 'frustrated', 'fugazi', 'fulfilled', 'fulton', 'fumbling', 'fund', 'funk', 'furious', 'furry', 'furs', 'fuse', 'fuzz', 'fuzzing', "g'd", 'gadget', 'gadgets', 'gaga', 'gagging', 'gained', 'gaining', 'gala', 'gallon', 'galore', 'gambino', 'gangbang', 'gangbangers', 'gangland', 'gangs', 'gangsters', 'garages', 'garfield', 'garlic', 'garvey', 'gasket', 'gasolina', 'gasoline', 'gassing', "gat's", 'gatekeepers', 'gators', 'gauge', 'gavel', 'gayer', 'gd', 'ge', 'gears', 'geekers', 'geezy', 'gemini', 'genes', 'gentle', 'genuine', 'gerber', 'german', 'germany', 'gesture', 'getcha', 'ghostwriters', 'gianni', 'gibson', 'gifted', 'gifting', 'gigantic', 'gillespie', 'gillette', 'gimmick', "girlfriend's", 'girlfriends', 'girly', 'glaciers', 'gladiators', 'glam', 'glamour', 'glare', 'glassy', 'glaziers', 'gleam', 'glide', 'glider', 'gliding', 'glimpse', 'glitch', 'glitz', 'gloomy', 'gloss', 'glossing', 'glove', 'glover', 'gnarly', 'goalie', 'goatee', 'goats', 'gobbler', 'goblins', 'godless', 'gogh', 'goldie', 'golfer', 'goodbyes', 'goodyears', 'goof', 'goofy', 'google', 'goop', 'gopher', 'gos', 'goth', 'grabbed', 'grace', 'grad', 'graduation', 'grady', 'grammar', 'grandad', 'grandaddy', 'grandchildren', 'granddaddy', "grandmother's", 'grandson', "granny's", 'grant', 'granting', 'graphic', 'graveyard', 'greasier', 'greed', 'greeter', 'gremlin', 'griffey', 'griffin', 'grimy', 'grin', 'gringo', 'grinning', 'griping', 'gripped', 'grizzlies', 'groom', 'grouped', 'grouping', 'growth', 'guacamole', 'guaped', 'guards', 'guest', 'guestroom', 'guests', 'guidance', 'guilt', 'guineas', 'guinness', 'gunners', 'gunning', 'gunplay', 'gunpowder', 'gushing', 'gwaluh', 'habits', 'hack', 'hacker', "hair's", 'haircut', 'hairlines', 'hairy', 'haitians', 'halftime', 'hallelujah', 'hallie', 'halves', 'hamilton', 'hamptons', 'handcuffed', 'handed', 'handgun', 'handled', 'handles', 'handling', 'hangers', 'hannibal', 'hansom', "happen's", 'happier', 'happiness', 'harbor', 'hardest', 'harding', 'hardtop', 'harp', 'harshest', 'harvard', 'hashtag', 'hasta', 'hatch', 'hatchback', 'hatchets', "hater's", 'hatred', 'haunting', 'haw', 'hawks', 'hazy', 'hbo', 'headband', 'header', 'headers', 'heading', 'headlight', 'headlights', 'headliner', 'heal', 'healed', 'heap', 'heartbeat', 'heartbreak', 'heartbreaker', 'heaters', 'heathen', 'heating', "heaven's", 'heavily', 'heavyweight', 'hebrew', 'hector', 'heed', 'heel', 'heff', 'heffner', 'heh', 'heights', 'heinous', "hell's", 'helmets', 'helper', 'henchmen', 'herb', 'herbal', 'hereditary', 'heroes', 'herr', 'hesitation', 'hibernate', 'hickeys', 'hid', 'hideout', 'hiffie', 'highland', 'highlight', 'highness', 'hike', 'himself', 'hindu', 'hinges', 'hint', 'historical', 'hitch', 'hitchhiking', 'hiting', 'hitler', 'hitmen', 'hm', 'hoarder', 'hoarse', 'hocus', "hoe'ing", 'hoeing', 'hoffman', 'hog', 'hogan', 'hogging', 'hokus', 'holds', 'holla', 'hollyhood', 'holmes', 'holocaust', 'holster', 'homecooking', 'homeless', 'homemade', 'homework', 'homicidal', 'honeymoon', 'hoods', 'hooker', 'hookers', 'hooky', 'hooping', 'hooters', 'hopeless', 'hopscotch', 'hornets', 'horns', 'horsed', 'horseshoe', 'hostage', 'hosting', 'hotness', 'hound', 'hourglass', 'housewives', 'housing', 'hovering', 'howl', 'hublots', 'huddle', 'hues', 'huffed', 'huffy', 'hula', 'hum', 'humanity', 'hump', 'humvee', 'hung', 'hunger', 'hunter', 'hunters', 'hurdle', 'hut', 'hydro', 'hyenas', 'hygienes', 'hyperventilate', 'hypnotic', 'hypnotize', 'hypnotized', 'ibuprofen', 'iceberg', 'icebox', 'iceland', 'icky', 'ida', 'identify', 'identity', 'idiot', 'ies', 'ig', 'ignited', 'igniters', 'ignorant', 'iguana', 'illinos', 'illuminates', 'imagined', 'immature', 'immediate', 'immigrant', 'immortal', 'immune', 'impala', 'impalas', 'implant', 'import', 'impressed', 'improbable', 'improve', 'improvement', 'improvise', 'incase', 'inching', 'incident', 'included', 'including', 'income', 'inconsistent', 'increase', 'index', 'indo', 'iner', 'infatuated', 'infatuation', 'infected', 'infidelity', 'infinity', 'inflated', 'inflicted', 'influence', 'influenced', 'influent', 'influenza', 'inhaling', 'injuries', 'inner', 'innovation', 'insect', 'insecurities', 'insecurity', 'insists', 'inspire', 'instigated', 'instrumental', 'insurance', 'intact', 'intercept', 'interest', 'intermission', 'international', 'interrupting', 'interviewed', 'intimate', 'intoxicated', 'intrigued', 'intro', 'introduced', 'introduction', 'intuition', 'invade', 'invaded', 'investigation', 'investing', 'invincible', 'invitations', 'ipod', 'iran', 'iraq', 'irish', 'irking', 'ironic', 'isis', 'italians', 'itch', 'itty', 'iverson', 'jabronis', 'jabs', 'jackets', 'jacking', "jackson's", 'jacksons', 'jacky', 'jacoby', 'jade', 'jaded', 'jags', 'jails', 'jal', 'jaleel', 'jamaican', 'jamba', 'january', "jaw's", 'jawless', 'jayhawks', 'jays', 'jazz', 'jealousy', 'jeepers', 'jeez', 'jefferson', 'jeffery', 'jennifer', 'jenny', 'jeopardize', 'jesse', 'jeter', 'jetski', 'jetskis', 'jetson', 'jetstream', 'jew', 'jewel', "jewelry's", 'jewelrys', 'jewish', 'jews', 'jigga', 'jiggers', 'jiggle', 'jiggy', 'jill', 'jingling', 'jit', 'jitsu', 'jocked', 'jodeci', 'joes', 'jog', 'joker', 'jokes', 'joking', 'jolly', 'journey', 'journeys', 'jowls', 'js', 'juggle', 'juggling', 'juju', 'julius', 'junk', 'junky', 'junkyard', 'jupiter', 'jurassic', 'jurist', "jury's", 'justifiably', 'juuged', 'juvenile', "k'ing", 'kaboom', 'kale', 'kamikazee', 'karl', 'katie', 'kats', 'keepers', 'kemosabe', 'kennedy', 'kennedys', 'kensli', 'kenzo', 'ketchup', 'kettle', 'khloe', 'kia', 'kicker', 'kickstand', 'kiddies', 'killtech', 'kilt', 'kimberly', 'kimbo', 'kimosabe', 'kinda', 'kingpin', 'kingston', 'kinte', 'kirkland', 'kitchens', 'kite', 'kites', 'kits', 'kitted', 'kiwi', 'kkk', 'klein', 'klumps', 'knick', 'knight', 'knives', 'knockers', 'knockoff', 'knockout', 'knocks', 'knucklehead', 'knuckles', 'koala', 'koalas', 'kroger', 'kyrie', 'la', 'laces', 'lacing', 'lacs', 'lading', 'lagger', 'lames', 'lance', 'lancer', 'landlord', 'lantern', 'laps', 'laptop', 'larger', 'largo', 'laser', 'lasik', 'lasts', 'latching', 'latex', 'lather', 'lawsuit', 'layaway', 'layed', 'leaches', 'leads', 'learning', 'lease', 'ledge', 'leeches', 'leftovers', 'legacy', 'leggings', 'leno', 'leo', 'leopard', 'lesbi', 'lesley', 'lesser', 'letterman', 'letters', 'lever', 'lewis', 'lexus', 'liability', 'liberty', 'library', 'lice', 'licensed', 'licky', 'lifeguard', 'lifted', 'lighten', 'lighthouse', 'liking', 'lilo', 'limitation', 'limitings', 'limits', 'limp', 'lincoln', 'lindsay', 'lineback', 'linger', 'linguine', 'linguini', 'linked', 'lions', 'liquorice', 'lis', 'listened', 'listerine', 'littest', 'littles', 'litty', 'lobbies', 'lobsters', 'lockdown', 'lockjaw', 'logic', 'lohan', 'lollipops', 'lombardi', 'longevity', 'longitude', 'lookout', 'loosen', 'looser', "lord's", 'lorens', 'lorenzos', 'losie', 'loss', 'lotto', 'loubs', 'loudest', 'louisiana', 'louse', "love's", "lover's", 'lowered', 'lowest', 'lowry', 'ls', 'lucci', 'lucifer', 'lucked', 'lucks', 'luego', 'lugs', 'lukemi', 'lullaby', 'lunar', 'lurk', 'lust', "luther's", 'luxury', 'lv', 'lynched', 'lyrical', 'lyrics', 'macadamia', 'mace', 'machinery', 'machines', 'macintosh', 'madmen', 'magazines', 'magical', 'magnitude', 'magnums', 'mags', 'mains', 'majesty', 'majority', 'makaveli', 'malaysian', 'malcom', 'malice', 'malone', "mamma's", "man'", 'manager', 'managers', 'mandatory', 'maneuver', 'manicure', 'manicured', 'manning', 'manolo', "mansion's", 'mansions', 'manson', 'mantle', 'manual', 'manure', 'maple', 'marathon', 'marble', 'march', 'marcuses', 'marcy', 'margaritas', 'marge', 'mari', 'mariah', 'marinate', 'maris', 'marked', 'marker', 'marl', 'marleys', 'marriage', 'marrow', 'marsh', 'marshall', 'marshawn', 'mart', 'marta', 'martian', 'martians', 'marty', 'martyr', 'martyrs', 'marvel', 'marvin', 'maryland', 'marys', 'mascara', 'masquerade', 'massages', 'masseuse', 'mastermind', 'masturbated', 'masturbator', 'mathematician', 'matinee', 'matire', 'mattered', 'matthews', 'maui', 'maul', 'maverick', 'maxed', 'maximum', 'maxing', 'mayans', 'maybachs', 'mayonnaise', 'mcdonalds', 'mcgraw', 'mcguire', "me's", 'meadows', 'meagan', 'meaning', 'meantime', 'mecca', 'mechanics', 'medallions', 'meddling', 'media', 'medic', 'medication', 'meechy', 'meek', 'meeny', 'meeting', 'megan', 'megatron', 'mejor', 'melbourne', 'melted', 'members', 'memo', 'memorial', 'memories', 'memorize', 'memorized', 'menace', 'mentioned', 'mercedez', 'merch', 'merlot', 'mermaid', 'mesmerized', 'messaging', 'messed', 'messiah', 'messing', 'metalling', 'metamorphosis', 'methods', 'metropolitan', 'mets', 'mewtwo', 'mexicans', 'mg', 'michelin', 'mick', 'micky', 'microphone', 'micros', 'mics', 'middleman', 'midgets', 'midgrade', 'migliano', "mil'", "mil's", 'militia', 'milkman', 'millennium', 'millis', 'mimosas', 'mindful', 'minds', "mine's", 'minefield', 'mingle', 'mingling', 'minimal', 'miniskirts', 'minister', 'minus', 'miny', 'miracles', 'mirrors', 'misinformed', 'misread', 'missions', 'mist', 'mistreated', 'misunderstanding', 'mitch', 'mitsubishi', 'mitzvah', 'mixer', 'moan', 'moaning', 'mobile', 'mobsters', 'mock', 'modest', 'mogul', 'molasses', 'mold', 'molded', 'molest', "molly's", 'molotov', 'momentarily', 'momentum', 'mommy', 'monica', 'monogamy', 'monsoon', 'monsters', 'montage', 'montana', 'moody', 'moolah', 'mordor', 'morgue', 'morrison', 'mortal', 'mortgage', 'mossed', 'mot', "mother's", 'motions', "motivation'll", 'motorcycle', 'motorists', 'motto', 'mounds', 'mountains', 'mouths', 'movers', 'mozart', "mp's", 'mucus', 'muffling', 'mugged', 'mullet', 'multiply', 'mummy', 'munch', 'murderers', 'murders', 'murking', 'muscled', "music's", 'musically', 'mustafa', 'mute', 'mya', 'myspace', 'mysterio', 'mystery', "na's", 'nab', 'nacho', 'nachos', 'nagging', 'nameless', 'naming', 'napalm', 'napkins', 'napped', 'narcissistic', 'narcissists', 'narrow', 'nassau', 'nast', 'nationality', 'nations', 'natnat', 'nats', 'nauseated', 'naval', 'necessary', 'needles', 'neglected', 'neglection', 'negligence', "neighbor's", 'neighbours', 'nelly', 'neptune', 'nerds', 'nesting', 'nestle', 'network', 'neutered', 'neutral', 'neutrogena', 'nevada', 'nevermind', 'newly', 'newton', 'nexter', 'nicely', 'nicer', 'nickle', 'nickles', 'nicknamed', 'nighttime', "nike's", 'nile', 'nines', 'nineteen', "noah's", 'nonbeliever', 'nonchalant', 'nonsense', 'noodle', 'nookie', 'noose', 'norris', 'nosey', 'nostrils', "note's", 'notices', 'notifications', 'nra', 'nu', 'nuder', 'nudge', 'nuggets', 'numbered', 'numerous', 'nursery', 'nurtured', 'ny', "o'reilly", 'oat', "obama's", 'obamas', 'obese', 'observe', 'observing', 'obsolete', 'obstacles', 'occasion', 'occasions', 'offenders', 'offending', 'offense', 'offensive', 'offered', 'offers', 'officers', 'offing', 'offspring', "og's", 'oink', 'oldie', 'olive', 'olives', 'omar', 'omega', 'oncoming', 'onion', 'onions', 'online', 'onner', 'onto', "ooh'ing", 'ooze', 'operas', 'opinion', 'opinions', 'opponents', 'opposition', 'oral', 'ordering', 'orders', 'ore', 'oregon', 'oreo', 'orgies', 'origami', 'original', 'orlando', 'ornament', 'orphans', 'os', 'othello', 'outcome', 'outfits', 'outline', 'outs', 'outsides', 'outskirt', 'outweighing', 'oven', 'overachiever', 'overcharged', 'overcrowded', 'overdoing', 'overdose', 'overdosed', 'overdue', 'overexaggerating', 'overnight', 'override', 'oversees', 'overzealous', 'owen', 'owl', 'owning', 'oxygen', 'ozone', 'ozzy', 'pacers', 'pacific', 'pacino', 'package', 'packages', 'pacs', 'paddle', 'paddy', 'pads', 'pagani', 'pail', 'pains', 'paisley', 'pakistanis', 'pampers', 'panama', 'panarama', 'pancake', 'pander', 'panorama', 'panther', 'panti', 'pantry', 'papa', 'papoose', 'parachute', 'paralyze', 'paramedics', 'paranoia', 'pari', 'parka', 'parks', 'parlay', 'parliament', 'parole', 'parrots', 'participate', 'participation', 'particles', 'partied', 'parties', 'partly', "pasadena's", 'passengers', 'passes', 'password', 'paste', 'pastelle', 'pastors', 'pastries', 'pateks', 'paths', 'patricia', 'paws', 'payback', 'payed', 'payments', 'payout', 'paypal', 'pcs', 'pe', 'peach', 'peaches', 'pearl', 'pearls', 'peasant', 'pebbles', 'pecking', 'pedigrees', 'pedophile', 'peekaboo', 'peeled', 'peepholes', 'pelican', 'pellets', 'pendant', 'pending', 'penetrate', 'penguin', 'penicillin', 'penn', 'pennies', 'pension', 'peoples', 'peppermint', 'pepperonis', 'percolate', 'percy', 'perfecting', 'perfume', 'perimeter', 'peripheral', 'perpetrating', 'perplexing', 'persia', 'persistence', 'persistent', 'petite', 'petitioning', 'petrified', 'pg', 'phallus', 'phantoms', 'phantοm', 'pharmacist', "pharmacy's", 'phenomenon', 'phifer', 'philanthropy', 'philippine', 'phlegm', 'phoenix', 'photogenic', 'photography', 'phrase', 'physically', 'pic', 'picasso', 'picker', 'picks', 'pier', 'pigeon', 'piled', 'piles', 'pilgrims', 'pillar', 'pillows', 'pillsbury', 'pilots', 'pinching', 'pinker', 'pinkie', 'pinstripes', 'pinto', 'pip', 'pissy', 'pitchfork', "pitt's", 'pittsburg', 'pivot', 'pizzeria', 'piña', 'piñata', "place's", 'planetarium', 'plank', 'plant', 'plants', 'plaque', 'playground', 'playgrounds', 'playoff', 'plaza', 'pleased', 'pleases', 'plentiful', 'plentys', 'plotty', 'plucked', 'plural', 'plush', 'pocahontas', 'pocus', 'podcast', 'podium', 'poetic', 'pogo', 'pointed', 'pointing', 'points', 'poked', 'polish', 'politely', 'politicians', 'politicking', 'pollen', 'polos', 'pom', 'poms', 'pong', 'poof', 'pooled', 'poop', 'popeye', 'popper', 'poppers', 'populated', 'porridge', 'porta', 'portal', 'portfolio', 'portland', 'portrait', 'portraits', 'posh', 'posing', 'positions', 'possess', 'possession', 'possessive', 'possible', 'posting', 'posts', 'posture', 'potatoes', 'potent', 'pothead', 'pothole', 'potpourri', 'poulet', 'pounce', 'poverty', 'powerful', 'pp', 'prairie', 'prayed', 'prayers', 'pre', 'preachers', 'precise', 'precision', 'predator', 'predicted', 'prerogative', "prescription's", 'prescriptions', "president's", 'presidents', 'prestigious', 'pretended', 'prey', 'prezzies', 'pricey', 'prick', 'principal', 'pringles', 'priorities', 'prison', 'prisoner', 'privately', 'privates', 'probation', 'proceeding', 'produce', 'produced', 'producer', 'production', 'profile', 'profound', 'profusely', 'progress', 'prohibited', 'projected', 'promo', 'promote', 'promoters', 'prop', 'propaganda', 'propellers', 'propose', 'pros', 'prosper', 'prostituting', 'prototype', 'proved', 'provide', 'provoke', 'psychedelic', 'psychopathic', 'pt', 'pub', 'publicly', 'puffing', 'puffs', 'pukes', 'pulpit', 'pulse', 'pulses', 'pumps', 'pun', 'punching', 'punished', 'pupils', 'pups', 'purchased', 'pure', 'purest', 'pursuing', 'pusher', 'putang', 'pyramid', 'pyre', 'pyro', 'qb', 'quaaludes', 'quality', 'quarantine', 'quarantined', 'quart', 'quarters', 'queens', 'queers', 'questioning', 'quickly', 'quickness', 'quietly', 'quilt', 'quite', 'quitter', 'quitting', 'quo', 'quoting', 'rabies', 'raccoon', 'racists', 'rada', 'rafs', 'rafter', 'ragged', 'raging', 'raiding', 'railroad', 'raincoat', 'rainman', 'rakes', 'rally', 'rambling', 'ramen', 'ramming', 'ranchers', 'rank', 'ranked', 'rankings', "rap's", 'rapists', 'rascal', 'rash', 'rasta', 'rasting', 'ratatouille', 'rate', "rate's", 'ratio', 'rays', 'razorbacks', 'reached', 'reactions', 'reagles', 'realize', 'reap', 'reasons', 'rebellion', 'rebirth', 'rebound', 'recall', 'receding', 'receiving', 'recently', 'reception', 'recession', 'reckon', 'recognized', 'recommend', 'recorder', 'recycle', 'recycles', 'redded', 'redder', 'redefine', 'redemption', 'reeboks', 'reef', 'reefa', 'reevaluate', 'referee', 'reflection', 'reformed', 'refresh', 'refugee', 'refunds', 'regional', 'regis', 'regulations', 'reincarnated', 'reject', 'rejected', 'rejoiced', 'rekindle', 'relapse', 'relationship', 'relationships', 'relaxed', 'relaxing', 'released', 'relevant', 'reliable', 'relieve', 'reliving', 'reload', 'reloading', 'relocate', 'remarkable', 'remembers', 'reminding', 'reminds', 'reminisce', 'renaissance', 'rendezvous', 'renovations', 'renting', 'repair', 'repeal', 'repel', 'repellent', 'repent', 'repercussions', 'rephrase', 'replenish', 'repped', 'reptilian', 'reputations', 'require', 'rescue', 'research', 'reseat', 'reserve', 'reside', 'residence', 'residual', 'residuals', 'residue', 'resort', 'respected', 'respiratory', 'respond', 'responding', 'responsible', 'restaurant', 'resting', 'restore', 'restrain', 'retail', 'retirement', 'retro', 'retros', 'revelation', 'revenue', 'reverse', 'reviews', 'revived', 'revolutionary', 'revolvers', 'revolving', 'rhinestones', 'rhythm', 'ribs', 'ricardo', 'richest', 'richter', "rick's", "rico's", 'riders', 'ridiculous', 'righteous', 'ringer', 'risking', 'risks', 'ritalin', 'rito', 'ritual', 'riverdale', 'roadrunner', 'roads', 'roadster', 'roaring', 'roasted', 'robbery', 'robed', 'robing', 'robot', 'robotic', 'robotics', 'robster', 'rocca', 'rocked', 'rodents', 'rog', 'rollercoast', 'roman', 'romantic', 'rome', 'ronald', 'ronda', 'roofies', 'roofless', 'rookies', 'roommates', 'roosters', 'rootless', 'roots', 'rosemary', 'rot', 'rotten', 'roulettes', 'rounding', 'routine', 'routines', 'rove', 'rovers', 'rowboat', 'rows', 'royalty', 'rozay', 'rubi', 'ruckus', 'rugby', 'ruined', 'rulers', 'rumor', 'rumours', 'runnie', 'runt', 'rural', 'russell', 'rusty', 'rwar', 'ryu', 'sa', 'sabatoge', 'sabotage', 'sabre', 'sacked', 'sacramento', 'sacrificed', 'sacrifices', 'saddler', 'saddles', 'sail', 'sake', 'sally', 'salon', 'salsa', 'salutations', 'salvation', 'sample', 'sams', 'samurai', 'sanction', 'sandal', 'sandwich', 'sandwiches', 'sandy', 'sane', 'sangrias', 'sanity', 'sank', "santo's", 'santos', 'sap', 'sarah', 'sardines', 'sari', 'sat', 'satellite', 'saturn', 'savior', 'saviour', 'sawdust', 'sawed', 'scampi', 'scan', 'scandal', 'scandalous', 'scanner', 'scanning', 'scarcity', 'scattering', 'scent', 'schedules', 'scheme', 'schizophrenic', 'schooling', 'schwarzenegger', 'scissors', 'scoliosis', 'scoob', 'scoot', 'scorching', 'scored', 'scores', 'scotch', 'scottie', 'scram', 'scrambled', 'scraped', 'scraping', 'screenwrite', 'scribble', 'scripts', 'scroll', 'scroller', 'scrunch', 'scud', 'scuff', 'scuse', 'se', 'seafood', 'seagal', 'seagulls', 'seahorse', 'seamed', 'seamstress', 'seas', 'seashell', 'seashells', 'seaweed', 'secretary', 'secrets', 'seduced', 'seemed', 'seeming', 'seized', 'seizure', 'seldom', 'seller', 'semis', 'senile', 'senior', 'sensitive', 'separate', 'septum', 'sequel', 'serenade', 'serene', 'serial', 'serpent', 'servant', 'sesame', 'session', 'setback', 'setbacks', 'seventh', 'seventy', 'severe', 'sew', 'sewers', 'sewn', 'sexiest', 'sextape', 'sexton', 'shaded', 'shakes', 'shaky', 'shampoos', 'shanties', 'sharon', 'sharpening', 'shave', "she's", 'sheisty', 'shepard', 'sherbert', 'sherbet', 'sheriff', 'sherlock', 'sherman', 'shifts', 'shin', 'shiner', 'shipment', 'shitted', 'shivering', 'shootouts', 'shorter', "shot's", 'shouting', 'shouts', 'shove', 'showboat', 'shrinking', 'shudder', 'shutting', 'shuttles', 'sia', 'sic', 'sicily', 'sickening', 'sicker', 'sideburns', 'sideshow', 'sifting', 'silencer', 'silently', 'silhouette', 'silt', 'simpsons', 'sinatra', 'singers', 'sings', 'sinned', 'sinner', 'sinners', 'sinus', 'sipped', 'siren', 'sirens', 'sits', 'situation', 'situations', 'sizes', 'sketch', 'skillet', 'skills', 'skimpy', 'skirts', 'skittle', 'skittles', 'skys', 'skyscrapers', 'slammer', 'slang_words', 'slapping', 'slaps', 'slaved', 'slavery', 'slay', 'slayed', 'slayer', 'slaying', 'sleaze', 'sledgehammer', 'sleek', 'sleepless', 'sleepy', 'sleeved', 'sleeves', 'sleigh', 'sliced', 'slices', 'slicker', 'slid', 'slight', 'sliming', 'slimy', 'slipped', 'slips', 'slogan', 'slop', 'slowed', 'slowpoke', 'slug', 'slugs', 'slumber', 'slurp', 'slurping', 'slushy', 'slutting', 'smack', 'smarter', 'smartest', 'smear', 'smelled', 'smelly', 'smiths', 'smokes', 'smorgasbord', 'smother', 'smudge', 'snack', 'snacking', 'snaggle', 'snails', 'snapping', 'snares', 'sneaky', 'sneeze', 'sneezy', 'snickers', 'sniff', 'snipe', 'snobby', 'snorkeling', 'snorkling', 'snout', 'snowcone', 'snowed', 'snowmen', 'snub', 'snuck', 'soaked', 'sobriety', 'socal', 'soccer', 'socialist', 'socialists', 'socialize', 'society', 'sodas', 'softer', 'softly', 'soho', 'soil', 'solemnly', 'soles', 'solider', 'solitaries', 'somalian', 'somalians', 'someday', 'someway', "son's", 'songs', 'sony', 'sooner', 'sophisticated', 'sophistication', 'soppy', 'soprano', 'sopranos', 'sorrow', 'sort', 'sorted', 'sorting', 'souls', 'sounded', 'soups', 'southwest', 'spanking', 'spar', 'sparing', 'sparkles', 'sparkly', 'spasms', 'spears', 'species', 'specific', 'spectacular', 'speculation', 'spelling', 'sphinx', 'spicy', 'spiders', 'spiel', 'spilt', 'spinner', 'spiteful', 'spits', 'splain', 'splashy', 'splattered', 'spleen', 'splinters', 'splits', 'splurged', 'spokes', 'spooked', 'spoon', 'spooning', 'sportscenter', 'spouses', 'sprained', 'spreaded', 'spree', 'sprees', 'springer', 'sprinting', 'spritzer', 'squab', 'squash', 'squat', 'squeezing', 'squid', 'squinting', 'squirm', 'squirrel', 'squirting', 'stabbing', 'stadiums', 'staged', 'staggered', 'stains', 'stake', 'stale', 'stalkers', 'stamp', 'stamps', 'stan', 'standards', 'standings', 'standoff', 'stands', 'starburst', 'starch', 'stardom', 'stared', 'stares', 'stark', 'starship', 'starter', 'stashing', 'statements', 'stations', 'statues', 'statutory', 'std', 'steakhouse', 'steaks', 'steamboat', 'steamer', 'steaming', 'steer', 'steller', 'stencil', 'stephen', 'stephenson', 'steroids', 'stewart', 'stiches', "stick's", 'stilts', 'stinger', 'stings', 'stingy', 'stinking', 'stitch', 'stitched', 'stockings', 'stogie', 'stomachs', 'stomp', 'stoplight', 'stopper', 'stops', 'stopsign', 'stork', "story's", 'straighten', 'strain', 'strangling', 'stratosphere', 'strawberry', 'stray', 'streaks', 'stretching', 'stretchy', 'strict', 'stride', 'striker', 'stripe', 'stripped', 'strudel', 'strumming', 'stud', 'studded', 'studied', 'stuffing', 'stumble', 'stumbled', 'stumbles', 'stun', 'stunk', 'stunning', 'stutter', 'stylish', 'sub', 'subaru', 'subliminally', 'substance', 'subtract', 'suburb', 'suburban', 'suburbs', 'subway', 'sudoku', 'suede', 'suffer', 'suffocate', 'summersault', "sun's", 'sundae', 'sundress', 'sunken', 'sunrise', 'suns', 'superb', 'supermodel', 'supermodels', 'supper', 'supplier', 'supplying', 'surely', 'surgeries', 'surgical', 'surprises', 'surrounded', 'sus', 'suspect', 'sutra', 'sutures', 'suv', 'swagged', 'swallowing', 'swallows', 'swamp', 'swaps', 'swats', 'sway', 'sweaters', 'sweats', 'sweden', 'swedish', 'sweets', 'swerved', 'swimwear', 'swine', 'swiping', 'swishes', 'swiss', 'switches', 'swollen', 'swordfish', 'sworn', 'symbol', 'sympathy', 'symptoms', 'synthetic', 'syringes', 'syringing', "syrup's", "t's", 'ta', 'tackled', 'tactics', 'tagged', 'tailing', 'tainted', 'tainting', 'taipei', "takeoff's", 'takeover', 'takers', 'tale', 'tales', 'talker', 'talkie', 'tallying', 'tamara', 'tambourine', 'tampon', 'tangerine', 'tanned', 'tanning', 'tantalizing', 'tantrum', 'tantrums', 'taped', 'tar', 'targets', 'tartar', 'tassel', 'tasting', 'tate', 'tater', 'tattooed', 'te', "teacher's", 'teardrop', 'teardrops', 'tearing', 'technical', 'technically', 'technicals', 'teen', 'teenager', 'teeny', 'teething', 'telemundo', 'telepathic', 'temp', 'temporary', 'tenant', 'tendencies', 'tenderoni', 'tense', 'terminator', 'terribly', 'territory', 'testimony', 'testing', 'texts', 'thanked', 'theirs', 'theodore', 'therapy', "there'll", "they'd", 'thicky', 'thirteen', 'thoughta', 'thousandth', 'thowed', 'threesome', 'thrift', 'throttled', 'throttles', 'throwaways', 'thrower', 'throws', 'thump', 'thumping', 'thursday', "thursday's", 'tiarra', 'tic', 'ticked', 'tiers', 'tif', "tiffany's", 'tightened', 'tightness', 'tijuana', 'tilt', 'timber', 'timberland', 'timeout', 'tiny', 'tiqua', 'tit', 'titos', 'tl', 'toasted', 'toasts', 'tobacco', 'toddlers', 'tofu', 'tokens', 'tolling', 'toned', 'toni', "tonight's", 'tonsils', 'toothed', 'toothpaste', 'tootsie', 'topless', 'topped', "topper's", 'topping', 'toppings', 'toppling', 'tops', 'torching', 'tore', 'tornado', 'tortilla', 'tortoise', 'tot', 'totally', 'totem', 'toucan', 'tours', 'tow', "towel's", 'towels', 'tower', 'towering', 'toxic', 'toying', 'traction', 'trafficking', 'trailer', 'trained', 'training', 'traits', 'tramp', 'trance', 'transfer', 'transform', 'translate', 'translation', 'transmission', 'transport', 'transportation', 'trapezoid', 'trashy', 'traveled', 'travelling', 'treadmill', 'treasures', 'treating', 'treetop', 'trench', 'trends', 'trespassing', 'tribeca', 'tricked', 'trickery', 'trident', 'trike', 'trillest', 'trimmed', 'trimming', 'trinidadian', 'trojan', 'trojans', 'trooper', 'troopers', 'trophies', 'tropical', 'tropics', 'trousers', 'trout', 'trucker', "trunk'", 'trusted', 'truthfully', 'tsubi', 'tt', 'tub', 'tucking', 'tuesday', "tuesday's", 'tugboat', 'tum', 'tummy', 'tun', 'tunafish', 'tuner', 'turban', 'turd', 'turmoil', 'turner', 'tusk', 'tutor', 'tux', "tv's", 'twighlight', 'twitch', 'twitching', 'twitpic', 'twix', 'twο', 'tycoon', 'tying', 'tylenol', 'types', 'typical', 'typing', 'u', 'ufo', 'ultra', 'umpire', 'unalterably', 'unannounced', 'unapologetic', 'uncles', 'uncomfortable', 'undecided', 'undeniable', 'underarms', 'underground', 'underrated', 'understatement', 'understood', 'underwater', 'underwhelming', 'underworld', 'undressing', 'unemployed', 'uneven', 'unfairly', 'unfinished', 'unfold', 'unfortunate', 'uniform', 'unit', 'unkindly', 'unleashing', 'unlike', 'unmarried', 'uno', 'unreliable', 'unrequited', 'unruly', 'unseen', 'unstoppable', 'untamed', 'unto', 'unwind', 'unworthy', "up's", 'up;', 'uploading', 'upper', 'uppercuts', 'upside', 'upstairs', 'uranus', 'urine', 'usa', 'users', 'uzis', 'va', 'vac', 'vacay', 'valedictorian', 'value', 'vampires', 'vanish', 'vanity', "varsity's", 'vehicles', 'vein', 'velour', 'venetian', 'venezuela', 'venting', 'vera', 'verdict', 'verge', 'vernace', 'versaces', 'versatile', 'version', 'versus', 'vest', 'veteran', 'vi', 'via', 'viagra', 'vibrate', 'vibrating', 'vicariously', 'vices', 'vicious', 'vicodins', 'victorious', 'videos', 'viet', 'vietnam', 'viewing', 'views', 'viking', 'vikings', 'village', 'villainous', 'villains', 'ville', 'violation', 'violets', 'violin', 'violins', 'viper', 'visibly', 'visionary', 'visioning', 'visions', 'visor', 'vital', 'vitals', 'vivid', 'vizine', 'vocal', 'vogues', 'voilà', 'volcano', 'volunteers', 'vouchers', 'vows', 'vrooming', 'vs', 'vv', 'wacked', 'waddup', 'wade', 'wafers', 'wagons', 'waited', 'waiters', 'waldorf', 'walkie', 'wallace', 'wallets', 'wallpaper', "walter's", 'waner', 'wanna', 'warder', 'wardrobe', 'warehouse', 'warlord', 'warner', 'warning', 'warrant', 'warrants', 'warrior', "was'", 'wasabi', 'washer', 'washing', 'washingtons', 'watered', 'waterfall', 'waterglass', 'watering', 'waters', 'watts', 'waving', 'wavy', 'way;', "wayne's", 'waynes', 'weaves', 'weaving', 'webbie', 'weddings', 'wedgie', 'weegee', 'weekends', 'weenie', 'weep', 'weighs', 'wen', 'western', 'westside', 'wetting', 'whacking', 'whale', 'wham', 'whamming', "whatever's", 'wheaties', 'wheelers', 'wheezy', "when's", 'whichever', 'whisker', 'whiskers', 'whiskey', 'whiter', 'whoopi', 'whoozy', 'whopped', 'whos', "why'd", 'wi', 'widow', 'wildcat', 'wildebeest', 'wilder', 'wildest', 'wildfire', 'wildness', 'willis', 'winding', 'windmill', 'winds', 'wining', 'winnings', 'winslows', "winter's", 'wiped', 'wiping', 'wires', 'wisdom', 'wisely', 'witherspoon', 'wizard', 'woes', 'wonderland', 'wops', 'wordplay', 'work;', 'worker', 'workers', 'workout', 'workplace', 'works', "world's", 'worthless', 'wrestler', 'wright', 'wrinkled', 'wristwatch', 'writer', 'writing', 'wyoming', 'xxl', 'yagi', 'yam', 'yankee', 'yappa', 'yapping', 'yawn', 'yawning', 'yays', 'yb', 'yea', 'yeller', 'yolanda', 'yonder', 'yoppas', 'yopper', 'ys', 'yucatán', 'yuck', 'yup', 'z', 'zags', 'zeppelin', 'zipped', 'zippers', 'zircon', 'zoey', 'zoom', 'zulu']

word_fixes = {
    "nu": "new",
    "dis": "this",
    "ta": "the",
    "lames": "bitches",
    "skrip": "strip",
    "krazy": "crazy",
    "caucasians": "white",
    "nike's": "nikes",
    "he's": "he",
    "she's":"she",
    "ova":"over",
    "skees": "skis",
    "politicians": "politician",
    "caucasian": "white",
    "boy's": "boys",
    "cha": "your",
    "grandaddy": "granddaddy",
    "quarantined": "quarantine",
    "em": "them",
    "hansom": "handsome",
    "girlfriend's": "girlfriend",
    "thoughta": "thought",
    "robed": "robbed",
    "wit": "with",
    "girly": "girl",
    "cuss": "cause",
    "girlfriends": "girlfriend",
    "sho": "sure",
    "wanner": "wanna",
    "kats": "cats",
    "jury's": "jury",
    "eww": "ew",
    "officers": "cops",
    "phallus": "cock",
    "baddies": "bad",
    "fuzz": "cops",
    "kemosabe": "kimosabe",
    "neighbor's": "neighbor",
    "asses": "ass",
    "jewerly's": "jewerly",
    "jetskis": "skis",
    "gwaluh": "guala",
    "deers": "deer",
    "aah": "ah"
}
def replace_words(words):
    song_urls = get_song_url_list()
    for link in song_urls:
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for line in lyrics:
            for index, w in enumerate(line):

                if w in words:
                    print(w)
                    fix = words[w]
                    print(fix)
                    response = word_table.get_item(
                        Key = {
                            'id': fix
                        }
                    )
                    if 'Item' in response:
                        num_occurrences = response["Item"]['num_occurrences']
                        print(link)
                        print(line)
                        scraper.update_table(word_table, fix, "num_occurrences", (num_occurrences+1))
                        line[index] = fix
                        print(line)
                        scraper.update_table(song_table, link, "lyric_array", lyrics)

def create_last_word_dict():
    song_urls = get_song_url_list()
    word_list = []
    word_dict = {}
    Item = {}
    Item['id'] = "last_words"
    Item['words'] = {}
    for link in song_urls:
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for line in lyrics:
            if len(line) > 2:
                last_word = line[len(line)-1]
                print(line)
                if last_word not in word_list:
                    word_list.append(last_word)
                if last_word not in word_dict:
                    word_dict[last_word] = 1
                else:
                    word_dict[last_word] = word_dict[last_word] + 1

    viable_words = find_viable_words()
    for word in sorted(word_list):
        if word in viable_words:
            Item['words'][word] = word_dict[word]
    word_relation_table.put_item(
        Item=Item
    )

    print(Item)

def choose_last_word():
    response = word_relation_table.get_item(
        Key = {
            'id': "last_words"
        }
    )
    last_words = dict(response['Item']['words'])
    total = 26124
    randint = random.randint(0,total)

    sum = 0
    for word in last_words:
        sum += last_words[word]
        if sum >= randint:
            return word

def probability_roll(dictionary: dict):
    sum = 0
    word_list = []
    for item in dictionary:
        word_list.append(item)
        sum+=int(dictionary[item])
    randint = random.randint(1, sum)
    dice = 0
    #print("randint: {}".format(randint))
    for word in word_list:
        dice+=int(dictionary[word])
        #print(dice)
        if dice >= randint:
            return word
def build_word_relations():
    song_urls = get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}

    for link in song_urls:
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                if w not in viablewords:
                    lyrics[index][index2] = ""
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                line_parse(index2, line, relation_dict, word_list)

    for word in word_list:
        Item1 = {
            'id': str(word+"_1"),
            "words": relation_dict[word][str(word+"_1")]
        }
        Item2 = {
            'id': str(word + "_2"),
            "words": relation_dict[word][str(word+"_2")]
        }
        Item3 = {
            'id': str(word + "_3"),
            "words": relation_dict[word][str(word+"_3")]
        }
        word_relation_table.put_item(
            Item = Item1
        )
        word_relation_table.put_item(
            Item=Item2
        )
        word_relation_table.put_item(
            Item=Item3
        )

def line_parse(index: int, line: list, dictionary: dict, word_list: list):
    if index + 2 >= len(line):
        return
    word_1 = line[index + 2]
    word_2 = line[index + 1]
    word_3 = line[index]

    if word_1 == "" or word_2 == "" or word_3 == "":
        return

    if word_1 not in dictionary:
        dictionary[word_1] = {
            str(word_1 + "_1"): {

            },
            str(word_1 + "_2"): {

            },
            str(word_1 + "_3"): {

            }
        }
    if word_2 not in dictionary:
        dictionary[word_2] = {
            str(word_2 + "_1"): {

            },
            str(word_2 + "_2"): {

            },
            str(word_2 + "_3"): {

            }
        }
    if word_3 not in dictionary:
        dictionary[word_3] = {
            str(word_3 + "_1"): {

            },
            str(word_3 + "_2"): {

            },
            str(word_3 + "_3"): {

            }
        }
    if word_1 not in word_list:
        word_list.append(word_1)
    if word_2 not in word_list:
        word_list.append(word_2)
    if word_3 not in word_list:
        word_list.append(word_3)
    """         word_3       word_2     word_1"""
    if word_2 not in dictionary[word_1][str(word_1 + "_1")]:
        dictionary[word_1][str(word_1 + "_1")][word_2] = 1
    else:
        dictionary[word_1][str(word_1 + "_1")][word_2] =dictionary[word_1][str(word_1 + "_1")][word_2]+1
    if word_3 not in dictionary[word_1][str(word_1 + "_2")]:
        dictionary[word_1][str(word_1 + "_2")][word_3] = 1
    else:
        dictionary[word_1][str(word_1 + "_2")][word_3] =dictionary[word_1][str(word_1 + "_2")][word_3]+1
    if word_3 not in dictionary[word_2][str(word_2 + "_1")]:
        dictionary[word_2][str(word_2 + "_1")][word_3] = 1
    else:
        dictionary[word_2][str(word_2 + "_1")][word_3] = dictionary[word_2][str(word_2 + "_1")][word_3]+1
    if index + 3 >= len(line) or line[index+3] == "":
        return
    word_0 = line[index+3]
    if word_0 not in dictionary:
        dictionary[word_0] = {
            str(word_0 + "_1"): {

            },
            str(word_0 + "_2"): {

            },
            str(word_0 + "_3"): {

            }
        }
    if word_0 not in word_list:
        word_list.append(word_0)
    if word_3 not in dictionary[word_0][str(word_0 + "_3")]:
        dictionary[word_0][str(word_0 + "_3")][word_3] = 1
    else:
        dictionary[word_0][str(word_0 + "_3")][word_3] = dictionary[word_0][str(word_0 + "_3")][word_3]+1

def check_exists(id):
    response = word_relation_table.get_item(
        Key={
            "id": id
        }
    )
    if 'Item' in response:
        print(id + " exists")
        return True
    else:
        print(id + " doesn't exist")
        return False

def get_relation_dict(word: str, num: int):
    response = word_relation_table.get_item(
        Key = {
            "id": str(word+"_"+str(num))
        }
    )
    return dict(response['Item']['words'])

def find_union(dicts: list):
    union_list = []
    base_words = []
    word_count = {}
    for d in dicts:
        for word in d:
            if word not in word_count:
                word_count[word] = 1
            else:
                word_count[word]=word_count[word]+1
    for item in word_count:
        if word_count[item] == len(dicts):
            union_list.append(item)

    return(union_list)


def build_sentence(length: int):
    last_word = choose_last_word()
    sentence = []
    i = 0
    while i < length:
        sentence.append("")
        i += 1
    sentence[length-1] = last_word
    a = get_relation_dict(last_word, 1)
    #print(a)
    second_to_last_word = probability_roll(a)
    print(second_to_last_word)
    sentence[length - 2] = second_to_last_word
    i = length-3
    while i>=0:
        word_1=sentence[i+2]
        word_2 =sentence[i+1]

        #words 2 steps away and one step away respectively
        prev_words_2 = get_relation_dict(word_1, 2)
        prev_words_1 = get_relation_dict(word_2, 1)
        prev_word_list = [prev_words_1, prev_words_2]

        if(i+3)<length:
            word_0 = sentence[i+3]
            prev_words_3 = get_relation_dict(word_0, 3)
            prev_word_list.append(prev_words_3)


        try:
            potential_words = find_union(prev_word_list)

            sentence[i] = random.choice(potential_words)
            print("Union of {} spaces".format(str(len(prev_word_list))))
        except IndexError:


            sentence[i]=probability_roll(prev_words_1)
            print("Dice  Roll")
        i-=1
    print(sentence)




def line_parse_4(index: int, line: list, dictionary: dict, word_list: list):
    if index + 4 >= len(line):
        return
    word_1 = line[index + 4]
    word_2 = line[index + 3]
    word_3 = line[index+2]
    word_4 = line[index + 1]
    word_5 = line[index]

    if word_1 == "" or word_2 == "" or word_3 == "" or word_4 == "" or word_5 == "":
        return

    if word_1 not in dictionary:
        dictionary[word_1] = {
            str(word_1 + "_4"): {

            }
        }
    if word_1 not in word_list:
        word_list.append(word_1)

    """word_5     word_4     word_3      word_2     word_1"""
    if word_5 not in dictionary[word_1][str(word_1 + "_4")]:
        dictionary[word_1][str(word_1 + "_4")][word_5] = 1
    else:
        dictionary[word_1][str(word_1 + "_4")][word_5] =dictionary[word_1][str(word_1 + "_4")][word_5]+1

def build_word_relations_4():
    song_urls = get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}

    for link in song_urls:
        print(link)
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                if w not in viablewords:
                    lyrics[index][index2] = ""
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                line_parse_4(index2, line, relation_dict, word_list)
    print(len(word_list))
    for word in word_list:
        Item = {
            'id': str(word + "_4"),
            "words": relation_dict[word][str(word + "_4")]
        }
        word_relation_table.put_item(
            Item=Item
        )
        print("added {}".format(word))


