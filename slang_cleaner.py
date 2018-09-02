
import boto3
from PyDictionary import PyDictionary
dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
dictionary=PyDictionary()

def remove_weirdness(word: str)->str:
    """Removes bad characters from words"""
    word = word.replace("β", "b")
    word = word.replace("ι", "i")
    word = word.replace("ε", "e")
    word = word.replace("τ", "t")
    word = word.replace("α", "a")
    word = word.replace(";", "")
    word = word.replace(')', "")
    return word

def clean_misspellings(word: str)-> str:
    if len(word) < 1:
        return ""
    if word == 'infatutation':
        word = "infatuation"
    if word == 'peringnon':
        word = 'perignon'
    if word == 'cacoon':
        word = "cocoon"
    if word == 'jxm':
        word = "jim"
    if word == "somethings":
        word = "something"
    if word == "she's":
        word = "she"
    if word == "shawt":
        word = "shawty"
    if word == "icey":
        word = "icy"
    if word == "everyone's":
        word = "everyone"
    if word == "f**kin" or word == "f***ing" or word == 'fuckiin':
        word = "fucking"
    if word == "aligator":
        word = "alligator"
    if word == "traping":
        word = "trapping"
    if word == "chickin'":
        word = "chicken"
    if word == "mammi" or word =="mommy":
        word = "mami"
    if word == "shes":
        word = "she"
    if word == "juciy":
        word = "juicy"
    if word == "shorty":
        word = "shawty"
    if word == "shyt" or word == 's**t':
        word = "shit"
    if word == "shyts":
        word = "shits"
    if word == "wett":
        word = "wet"
    if word == "wiegh":
        word = "weigh"
    if word == "witht":
        word = "with"
    if word == "bollar":
        word = "baller"
    if word == "commas'll":
        word = "commas"
    if word == 'f*ck' or word == 'f**k' or word ==  'fvck' :
        word = "fuck"
    if word == 'f*cked' or word == 'f**ked':
        word = 'f*cked'
    if word == 'f*cking' or word == 'f**king' or word ==  'fvcking':
        word = "fucking"
    if word == 'motherf*cker':
        word = 'motherfucker'
    if word == "p*ssy":
        word = "pussy"
    if word == "patron" or word == "patrone":
        word = 'patrón'
    if word == 'bi**h':
        word = "bitch"
    if word == 'embarassing':
        word = "embarrassing"
    if word == 'homi':
        word  = "homie"
    if word == 'masarati':
        word = "maserati"
    if word == 'rarri':
        word = "rari"
    if word ==  'piru':
        word = "peru"
    if word == 'crusing':
        word = "cruising"
    return word

def clean_slang(word: str) -> str:
    """Text cleaning for slang words, turns them into proper english"""
    if len(word) < 1:
        return ""
    if word == "thin":
        return "thin"
    try:
        if (word[len(word) - 3:]) == "in\'":
            word = word[:len(word) - 1] + "g"
        else:
            if word[len(word)-1]=='\'':
                word = word[:len(word)-1]
        if (word[len(word) - 2:]) == "in" and is_slang(str(word+"g")) is False:
            word += "g"
        if (word[len(word) - 2:]) == "la" and is_slang(word[:len(word)-1]+"er") is False:
            word = str(word[:len(word)-1]+"er")
        if (word[len(word) - 3:]) == "las" and is_slang(word[:len(word)-1]+"ers") is False:
            word = str(word[:len(word)-1]+"ers")
        if (word[len(word) - 2:]) == "na" and is_slang(word[:len(word)-1]+"er") is False:
            word = str(word[:len(word)-1]+"er")
        if (word[len(word) - 3:]) == "nas" and is_slang(word[:len(word)-1]+"ers") is False:
            word = str(word[:len(word)-1]+"ers")
        if (word[len(word)-1:]) =="z" and is_slang(str(word[:len(word)-1]+"s")) is False:
            word = str(word[:len(word)-1]+"s")
        if (word[len(word) - 2:]) == "da" and is_slang(str(word[:len(word)-1]+"er")) is False:
            word = str(word[:len(word)-1]+"er")
        if (word[len(word) - 3:]) == "das" and is_slang(str(word[:len(word)-1]+"ers")) is False:
            word = str(word[:len(word)-1]+"ers")
    except IndexError:
        pass
    if word == "dawg" or word == "dogg":
        word = "dog"
    if word == "aint":
        word = 'ain\'t'
    if word == "bangaz":
        word = "bangers"
    if word == "balla":
        word = "baller"
    if word == "blak":
        word = "black"
    if word == "bytches" or word == 'bihes' or word == "bitch's":
        word = "bitches"
    if word == "chu" or word == "u":
        word = "you"
    if word == "choosen":
        word = "choosing"
    if word == "fingaz" or word == "finggaz":
        word = "fingers"
    if word == "fuk":
        word = "fuck"
    if word == "fukin":
        word = "fucking"
    if word == "hamma":
        word = "hammer"
    if word == "im":
        word = "i'm"
    if word == "motha":
        word = "mother"
    if word == "thang":
        word = "thing"
    if word == "ya" or word == "yea" or word == 'yah' or word == 'yahhh' or word == "yeh" or word == 'yeaaaaah' or word == 'yeaaah' or word == 'yee' or word == 'yeeeeeeea' or word == 'yeeeeeeeeeeaa':
        word = "yeah"

    if word == "gangstaz":
        word = "gangsters"
    if word == 'fuckn':
        word = "fucking"
    if word == "finna":
        word = "gonna"
    if word == "psych":
        word = "psyche"
    if word == "playa":
        word = "player"
    if word == "o" or word == 'ohhhh':
        word = "oh"
    if word == "naw":
        word = "nah"
    if word == "killas":
        word = "killers"

    if word == "tonite":
        word = "tonight"
    if word == "tryina" or word == "trina":
        word = "tryna"
    if word == "til":
        word = "till"
    if word == "thats":
        word = "that's"
    if word == "stoopid":
        word = "stupid"
    if word == "dont":
        word = "don't"
    if word == "codine":
        word = "codeine"
    if word == "biatch":
        word = "bitch"
    if word == "ay" or word == "ey" or word == 'ayy' or word == 'ayyy':
        word = "aye"

    if word == "whats":
        word = "what's"
    if word == "yer":
        word = "your"
    if word == "coup" or word == 'coupé':
        word = "coupe"

    if word == "ballas":
        word = "ballers"

    if word == "boi":
        word = "boy"
    if word == 'buisiness' or word == 'bussiness':
        word = 'business'

    if word == "comming":
        word = "coming"
    if word == "everythang":
        word = "everything"
    if word == "cush":
        word = "kush"
    if word == "flo":
        word = "flow"
    if word == "dollas":
        word = "dollers"
    if word == "drumma":
        word = "drummer"
    if word == "giuseppe's":
        word = "giuseppes"
    if word == "hustlas":
        word = "hustlers"

    if word == "i'mma" or word == "ima" or word == "imma":
        word = "i'ma"
    if word == "ive":
        word = "i've"
    if word == "jewerly" or word == 'jewlery':
        word = "jewelery"

    if word == "jus":
        word = "just"
    if word == "mothafucka" or word == 'muthafucka' or word == 'motherfucka':
        word = "motherfucker"
    if word == "mothafuckas" or word == 'muthafuckas':
        word = "motherfuckers"
    if word == "otha":
        word = "other"
    if word == "neice":
        word = "niece"
    if word == "nex":
        word = "next"
    if word == "lo":
        word = "low"


    if word == "partment":
        word = "apartment"
    if word == "wasnt":
        word = "wasn't"

    if word == "ight" or word == "ite" or word == "aite":
        word = "aight"
    if word == "coochie":
        word = "cuchi"
    if word == "blu":
        word = "blue"

    if word == "climin":
        word = "climbing"

    if word == "dem":
        word = "them"
    if word == "dolla":
        word = "dollar"
    if word == "dollas":
        word = "dollars"
    if word == "feelin's" or word == "feelins":
        word = "feelings"
    if word == "ferrari's":
        word = "ferraris"
    if word == "forgiato's":
        word = "forgiatos"
    if word == 'hunned' or word == 'hunnid' or word == 'hunnit':
        word = "hundred"
    if word == 'kno':
        word = "know"
    if word == "masi":
        word = "mazzi"
    if word == "millionare":
        word = "millionaire"
    if word == 'shotties' or word == "shorties":
        word = "shawties"
    if word == "soulja":
        word = "soldier"
    if word == 'swagga':
        word = "swagger"
    if word == 'thugga':
        word = "thugger"
    if word == "thru":
        word = "through"
    if word == "try'na":
        word = "tryna"
    if word == "youngin's":
        word = "youngins"
    if word == "actavis" or word == 'activis':
        word = "activists"
    if word == "benji's" or word == "benjis":
        word = "benji"
    if word == "brodie":
        word = "brody"
    if word == "chillen":
        word = "chilling"
    if word == "dawgs":
        word = "dogs"

    if word == 'forrest':
        word = "forest"
    if word == "gots":
        word = "got"
    if word == "fuckboi" or word == "fuccboi":
        word = "fuckboy"
    if word == "gunn":
        word = "gun"
    if word == 'heyy' or word == 'heyyy':
        word = "hey"
    if word == "haitain":
        word = "haitian"
    if word == "homie's":
        word = "homies"
    if word == 'huhh':
        word = "huh"
    if word == 'hunnas' or word == "hunnids" or word == "hunnid's" or word == 'hundreads':
        word = "hundreds"
    if word == "kool":
        word = "cool"
    if word == 'mothafuck':
        word = "motherfuck"
    if word == 'mothafucker' or word == 'mothafucka':
        word = 'motherfucker'
    if word == 'mothafucking' or word == 'muhfucking' or word == "mo'fucking":
        word = "motherfucking"
    if word == 'motherf*ckers':
        word = "motherfuckers"
    if word == 'ohh' or word == 'ohhh':
        word = "oh"
    if word == 'oooo' or word == 'ooooh' or word == "oooh" or word == 'ooo' or word == 'ooohh' or word == 'oohh':
        word = "ooh"
    if word == "oop":
        word = "oops"

    if word == "pollie":
        word = "prolly"
    if word == 'sanging':
        word = "singing"
    if word == 'sensitiv':
        word = "sensitive"
    if word == 'shotters':
        word = "shooters"
    if word == "skoob":
        word = "scoob"
    if word == "snupe":
        word = "snoop"
    if word == "soo":
        word = "so"
    if word == 'spazz':
        word = "spaz"
    if word == 'sphagetti':
        word = "spaghetti"
    if word == "swoll":
        word = "swole"
    if word == "tha":
        word = "the"
    if word == "thes":
        word = "these"
    if word == 'trynna':
        word = "tryna"
    if word == "ugh" or word == "uhh":
        word = "uh"
    if word == 'vvss':
        word = "vvs's"
    if word == "whaat":
        word = "what"
    if word == "wrassle":
        word = "wrestle"
    if word == 'yall':
        word = "y'all"
    if word == "aaah" or word == 'ahh':
        word = "ah"
    if word == 'antartica':
        word = "antarctica"
    if word == "benzs" or word == "benz's":
        word = "benzes"
    if word == "billie":
        word = "billi"
    if word == "brrrr" or word == "brrt" or word =='brrrrt' or word == 'brp' or word == 'brrr':
        word = "brr"
    if word == "everday":
        word = "everyday"
    if word == "feening" or word == 'feinding':
        word = "fiending"
    if word == "flava":
        word = "flavor"
    if word == 'gabanna':
        word = 'gabbana'
    if word == 'gonn':
        word = "gon"
    if word == "gwap":
        word = "guap"
    if word == "hitta":
        word = "hitter"
    if word == 'hoo':
        word = "who"

    if word == 'ol':
        word = 'old'
    if word == "nuthing":
        word = "nothing"
    if word == 'knarly':
        word = "gnarly"
    if word == 'kombat':
        word = "combat"
    if word == "kourtney":
        word = "courtney"
    if word == "liks" or word == "liqs":
        word = "licks"
    if word == 'maaaan':
        word = "man"
    if word == "manhi":
        word = "mannie"
    if word == "moly":
        word = "molly"
    if word == 'pakistanians':
        word = "pakistanis"
    if word == "oxycont":
        word = "oxycontin"
    if word == "paronamic":
        word = "panoramic"
    if word == "patna":
        word = "parnter"

    if word == 'playas':
        word = "players"
    if word == "poppi" or word == "popi":
        word = "papi"
    if word == 'presidental':
        word = 'presidential'
    if word == 'skrrrttt' or word == 'skurt' or word == 'skrt' or word == 'skrr':
        word = "skrrt"
    if word == "rilo":
        word = "rillo"
    if word == "turky":
        word = "turkey"
    if word == 'vroooom':
        word = "vroom"
    if word == "balmain's":
        word = "balmains"
    if word == 'boujee' or word == 'bougies':
        word = "bougie"

    if word == 'choppas':
        word = "choppers"
    if word == "dey":
        word = "they"

    if word == "foreign's":
        word = "foreigns"
    if word == "glaw":
        word = "glaw"
    if word == 'growed':
        word = "grown"
    if word == 'grimlin':
        word = "gremlin"
    if word == "hancho":
        word = "huncho"
    if word == "hon":
        word = "hun"
    if word == 'hunna':
        word = "hundred"
    if word == 'independant':
        word = "independent"
    if word == "jeeper's":
        word = "jeepers"
    if word == "jetson's":
        word = "jetsons"

    if word ==  "jxmmi":
        word = "jimmi"
    if word == 'killler':
        word = "killer"
    if word == 'klout':
        word = "clout"
    if word == 'koolos':
        word = "culos"
    if word == 'lluminati' or word == 'luminati':
        word = "illuminati"
    if word == 'linsey':
        word = "lindsey"
    if word == 'magarita':
        word = "margarita"
    if word == 'makavelli':
        word = "makaveli"
    if word == 'mamcitas':
        word = "mamacitas"
    if word ==  "milli's":
        word = "millis"
    if word == 'movié':
        word = "movie"
    if word == 'muhammed':
        wod = "muhammad"
    if word == 'panamara':
        word = "panamera"
    if word == 'pjs':
        word = "pj's"
    if word == 'playaz':
        word = "players"
    if word == 'nino':
        word = 'niño'
    if word == 'ole':
        word = "old"
    if word  == 'skrippers':
        word = "strippers"
    if word == 'slo':
        word = "slow"
    if word == "withdrawl":
        word = "withdrawal"
    if word == "withdrawls":
        word = "withdrawals"
    if word == 'tru':
        word = "true"
    if word == 'zans':
        word = "xans"
    if word == 'yung':
        word = "young"
    if word == 'younging':
        word = "youngin"
    if word == "amerika":
        word =  "america"
    if word == 'babyyy':
        word = "baby"
    if word ==  'banditt':
        word = "bandit"
    if word == 'bently':
        word = "bentley"

    if word == 'bouta':
        word  = "boutta"
    if word == 'brah':
        word = "bruh"
    if word == 'brotha':
        word = "brother"
    if word == "bugatti's":
        word= "bugattis"
    if word  == 'burnas':
        word = "burners"
    if word == 'choopers':
        word = "choppers"
    if word == 'chyeah':
        word = "yeah"
    if word == 'ciroq':
        word = "ciroc"
    if word ==  'couldnt':
        word = "couldn't"

    if word == "cuf":
        word = "cuff"
    if word == 'eazy':
        word = "easy"
    if word == 'ehhh' or word == 'ehh':
        word = "eh"
    if word == 'eva':
        word = "ever"
    if word == 'freekey' or word == 'freeky':
        word = "freaky"
    if word == 'gettaaa' or word == 'gettaaaa':
        word = "getta"
    if word == 'gimicking':
        word = "gimmicking"
    if word == "grandmama's":
        word = "grandma"
    if word == 'gualla':
        word = "guala"
    if word == 'haaa' or word == 'hah':
        word = "ha"
    if word == 'henn':
        word = "henny"
    if  word == "her's":
        word = "hers"
    if word ==  "i'am":
        word = "i'm"
    if word == 'jify':
        word = "jiffy"
    if word == 'meeeee':
        word = "me"
    if word  == 'moola':
        word = "mula"
    if word == 'morhpine':
        word = "morphine"
    if word == 'mooovve':
        word = "move"
    if word == 'musik':
        word = "music"
    if word == 'nop':
        word = "nop"
    if word ==  'nuntin' or word == 'nuthin':
        word = "nothing"
    if word ==  'passangers':
        word = "passengers"

    if word == 'porcelean':
        word = "porcelain"
    if word ==  'uahh' or word == 'ughh' or word == 'uhhh' or word == 'uhhhh':
        word = "uh"
    if word == 'visably':
        word = "visibly"
    if word ==  'wateva':
        word = "whatever"
    if word == 'wat' or word == 'wot':
        word = "what"
    if word == 'tril':
        word = "trill"
    if word == 'accapella':
        word = "acapella"
    if word == 'bagg':
        word = "bag"
    if word == 'berzerk' or word =='bezurk':
        word = "berserk"
    if word == 'cheeze':
        word = "cheese"
    if word == 'eitha':
        word = "either"
    if word == 'gurl':
        word = "girl"
    if word == 'gooood':
        word = "good"
    if word == 'xannys':
        word = 'xannies'
    if word == 'dounut':
        word = "donut"
    if word == 'thangs':
        word = "things"
    if word == 'isnt':
        word = "isnt"
    if word =="how's":
        word = "how"
    if word == 'millie':
        word = "milli"

    if word == 'hotta':
        word = "hotter"
    if word == "cadillac's":
        word = "cadillacs"
    if word == 'errbody':
        word = "everybody"
    if word =='errday' or word == "everybody's":
        word = "everyday"
    if word == 'dammit':
        word = "damnit"
    if word == 'glo':
        word = "glow"
    if word == 'suckn':
        word = "sucking"
    if word == 'smokn':
        word = "smoking"

    return word

slang_words = ['a$ap', 'acroonym', 'adamn', 'adidas', 'agp', 'alief', 'alotta', 'angelos', 'angliana', 'aod', 'ashanti', 'asics',
               'assche', 'astroworld', 'aude', "babee'os", 'badmon', 'ballies', 'bambi', 'barbies', 'batmobile', 'beasting', 'betty', 'bezos',
               'biani', 'bigging', 'bimmer', 'bladee', 'blam', 'blanco', 'bleveland', "boi's", 'bompton', 'bonnaroo', 'boobie', 'booch',
               'boof', 'bool', 'boop', 'bougies', 'bracking', 'bungie', 'bunky', 'buttshots', "cadillac's", 'californication', "can'tchu", 'carti',
               'celly', 'chauffer', 'cheffing', 'chevelle', 'chik', 'chiraq', 'chosing', 'citgo', 'clicc', 'cobain', 'coldplay', 'collab', 'contin',
               'copperfield', 'countant', 'crowling', 'cudi', 'dammit', 'dap', 'darth', 'deen', 'dese', 'diethylamide', 'dimethyltryptamine', 'dinosaurus',
               'doheny', 'dollers', 'dolo', 'douple', 'dro', 'du', 'during', "ease'a", 'easee', 'ehre', 'elliot', 'eric', 'errbody', 'errday', 'feining', 'ferg',
               'ferragammo', 'fiending', 'fifa', 'fil', 'flacko', 'flamers', 'flashbangs', 'flirty', "flo's", 'flocka', 'foolie', 'forgiattos', 'forgies',
               'fugaz', 'fye', 'ghostface', 'gibral', 'giela', 'gigi', 'ginnies', 'ginóbili', 'gleesh', 'gleeshie', 'glo', 'glocky', 'goddy', 'gosha', 'greazy',
               'griselda', 'gta', 'gtbsbe', 'haha', 'harajuku', 'hasbeens', 'hearted', 'heimlich', 'helmut', 'herc', 'heresay', 'hil', 'hilfiger', 'hmm',
               'homescreens', 'homi', 'hundreads', 'icytwat', 'instrumentals', 'intenines', 'intertube', 'intonic', 'ish', 'issey', 'isssey', 'jabronis',
               'jacque', 'jacques', 'janeiro', 'janice', 'jermaines', 'jetpack', 'jheri', 'jiggas', 'jill', 'judy', 'justine', 'karts', 'keith', 'killavesi',
               'krayzie', 'kream', 'krueger', 'ksubi', 'kurt', 'laflame', 'lala', 'lamar', 'lambos', 'lang', 'larry', 'laxed', 'leandoer', "leandoer's", 'leany',
               'leanバック、', 'licky', 'lightskinned', 'lionel', 'listerine', 'lowkey', 'luh', 'lyft', 'lysergic', 'mano', 'marilyn', 'matics', 'maybachs',
               "mcdonald's", 'mclaren', 'mexiko', 'minajing', 'miyaki', "mo'fucking", 'moby', 'monica', 'motherfucka', 'motorola', 'muhfucking', 'mwah',
               'myaki', 'myles', 'narder', 'nem', 'nextel', 'nicki', 'nicole', 'nigg', 'nigga', "nigga's", 'niggas', 'niggga', 'nite', 'nudy', "nudy's",
               "o'clock", 'odom', 'ohhhh', 'olé', 'onto', 'oohh', 'opiated', 'opioid', 'opp', 'opps', 'optimo', 'oregan', "other's", 'ouh', 'outchea',
               'overstand', 'oxy', 'parment', 'pasé', 'pde', "peace'd", 'peaced', 'pedic', 'peds', 'peepee', 'percs', 'phelps', 'phenix', 'phil', 'pirus',
               'pitbull', 'playboi', 'plaît', "polo'd", 'poppa', 'prez', 'punanay', 'quavo', "raf'd", 'raffy', 'razr', 'rerock', 'rihanna', 'ritis', 'rockless',
               'rolly', 'rumpty', "s'il", 'sadboy', 'sadboys', 'saiyan', 'sak', 'saks', 'saly', 'sandyroad', 'schooly', 'scoping', 'sean', 'seh', 'seinfeld',
               'shaka', 'shakalu', 'shaked', 'sharon', 'shawties', 'sherita', 'shmurda', 'shotgunning', 'shript', 'shrooms', 'shyguy', 'sicko', 'simp', 'skrr',
               'slipn', 'sme', 'smokn', 'snapple', 'soleil', 'soning', 'spazed', 'st', 'stacy', 'stix', 'stockttown', 'suckafree', 'suckn', 'swirved', 'tempur',
               'terio', 'thaiboy', 'toolie', 'travi$', 'travis', 'triffling', 'triller', 'tsubi', 'underwhelming', 'vader', 'vatore', 'veeners', 'visine', 'vlone',
               'vous', 'vámonos', 'wah', 'waze', 'whaa', 'wheelie', 'whitearmor', 'wipping', 'wock', 'wokstar', 'wth', 'xanna', 'yammy', 'yao', 'yeahhh', 'yentown',
               'yesjulz', 'yoshi', 'yoyhi', 'yuck', 'yup', 'ここの魔所は良し', 'これが', 'イェ', '東京', '毎日冒険', '遣りたい事なら遣る','adamn', 'alladin', "asperger's",
               'assche', 'atari', 'aways', 'baow', 'benihana', "benihana's", 'benoit', 'blaow', 'boatster', 'brittney', 'buddakan', 'bummy', 'bustas', 'cadillac',
               'cardi', 'carlton', 'carti', 'chakra', 'cigarella', 'cleo', 'colgate', 'collab', 'commes', 'curatin', 'dammit', 'darkthrone', 'darth', 'dasani', 'debarge',
               'deffo', 'dej', "denise's", 'dialer', 'dougie', 'dro', 'ecco', 'elon', "everybody's", "exhaustin'i", 'feinding', 'fiending', 'fisker', 'flacko', 'flakka',
               'fourty', 'fredericksville', 'freebase', "g'ed", 'garçon', 'gilly', 'ginobili', 'glizzy', 'glo', 'gosha', 'gta', 'gtr', 'haha', 'hilson', 'iamsu', 'icarly',
               'iky', 'itty', 'jaleel', 'je', 'jodye', 'kailua', 'kel', 'kells', 'kenan', 'keri', 'kirby', 'knuck', 'ksubi', 'labeija', 'lambos', 'lim', 'lorde', 'luv',
               'mewtwo', 'mhm', 'mia', 'moet', 'moncler', 'nair', 'neil', "neiman's", 'nigga', 'niggas', 'nigo', 'nuck', 'oo', 'opps', 'paramore', 'penndot', 'percs',
               'perpella', 'pharrell', "pharrell's", 'phatty', 'phillip', 'playboi', 'porshe', 'quavo', 'radisson', "raf'd", 'raq', 'rubberbands', 'russ', 'ryan', 'seaters',
               'skeme', 'skrting', 'sliggity', 'slimey', 'smeagle', 'snapchats', 'spikey', 'squirtle', 'starboy', 'steven', 'sucky', 'swisha', 'thaiboy', 'tjop', 'tootah',
               'towards', 'tuddie', 'umm', 'unconcious', 'urkel', 'vader', 'vashtie', 'vic', 'visine', 'visvims', 'vivienne', 'vlone', 'vêtements', 'wintour', 'yaa', 'yoshi', 'yous']




ok_slang = ['blam', 'blanco',"bimmer",'lowkey','instrumentals','krueger','yup', 'yuck','haha','forgiattos', 'forgies', 'flirty',
    'triller', 'tsubi', 'underwhelming','sharon','onto','monica','maybachs','licky', 'listerine','larry','jill', 'judy','keith','jabronis',
    'itty','percs',  'mewtwo','jaleel','fiending','cleo', 'colgate', 'collab', 'cadillac','cadillacs','bustas','benihana', 'alladin', 'gta','wheelie', 'seinfeld'
    'netflix','mixtape','mitch','eliante','jiggy','maserati','mami','sorta','adidas','ashanti', 'asics','barbies', 'batmobile','angliana', 'bambi','during',
    'backstabbed', 'backstabbing', 'crip', 'crips','yoppas','yappa','sabatoge','extendos', 'febreeze', 'gangbangers','carpool','hotties','stan', 'southside',
    'sportscenter', 'stefani','stiches','twighlight','underarms', 'unto','versus','visioning', 'vizine', 'voilà','yuh','whose',  "they've",'alakazam',
    'paypal', 'pete','pinocchio','richter', 'rodham', 'rodney', 'rog', 'roger', 'ronald', 'ronda','oui', 'quo', 'rainman', 'rasting', 'tunafish',
    'marcy','mcqueen','megan', 'mel','michelin','milf','mossed', 'murcielago','natnat',  'nevermind','nope','omar','pastelle', 'patricia',
    'gianni','gotcha', 'grady', 'grammy','gudda','hari',   'jennifer', 'jesse', 'jetski','kaboom', 'kamikazee','lucked', 'macking', 'maison','mami'
    'drumset', 'duffled','ecstacy', 'eddie','eh', 'ella', 'emoji','espn','frostbit','fubu','garvey', 'gerber','getcha', 'getta',
    "c'mon",'camacho', 'chete', 'chiquita', "choppers", 'cig', 'cinnabon','cita','cuffer','damian','deebowing','dipset',
'barbara',  'bartending', 'basquiat', 'bbq','bedsheets', 'beetlejuice', 'biggies', 'birdplay','bluetooth','boink',
    'adidas','amongst', 'angelina', 'aniston','applebees', 'appétit', "aren't",'ashley','badaboom', 'baden', 'balenci',
    'tif', 'tina', 'toppy', 'trendsetter', 'trendsetters','truckload','tunechi', 'turbos','ziploc', 'zoey',"youngin",'woah','yoda', 'yonce',
    'vera', 'vernace', 'via', 'vicodin','viet', 'ville', 'waterglass', "weren't", "when's",   'whichever', "why'd", 'wishy',
    'slutting','snowcone', 'socal', 'stats', 'steve',   'thotty','subliminally','taki', 'talo', 'tamara','thicky', 'thots','twerking', 'twix',
    'northside',"o'reilly", 'oc', "og's",'oj','pagani','qb','puerto','rito', 'rocca', 'rockstar','rosés','rosé', 'ryu', 'schwarzenegger', 'screenwrite',
    'perkys','phifer','philly', 'pikachu', 'pillsbury',  'pissy','piña', 'piñata', "pj's",'playstation', 'pocus', 'pogo','pookie', 'popeyes','oprah','niño',
    "millis",'miny', 'miyagi', 'moonrocks', 'mordor','mtv', 'nate', 'nats','nemo', 'neutrogena','nickles','ot','ozzy','pagani','panarama','payout', 'perc',
    "illuminati",'lombardi', 'louboutins', 'luego','macarena',"makaveli", 'marcus', 'marshawn', 'marty', 'marvin', 'matata', 'mazi', 'mcguire', 'meeny', 'megatron', 'mejor',
    'kareem', 'katie', 'katrina', 'kd','kimberly',"culos","culo",'layaway', 'lenox', 'lexus', 'lineback', 'linsey', 'lisa', 'litty', 'lizzy','lou', 'louboutin','eeny',
    'hoodie', 'hov', 'hugh','iggy',"it'd", 'iverson', 'jackie', 'jacuzzi',"jeepers",'jetstream', 'jigga', 'jim', 'jit', 'jodeci', 'joes', 'julius', 'juuged',
    'glah', 'glocks', 'grimlin',  'gullah','hanna', "hasn't", "haven't", 'heff', 'heffner', 'helipad','himself', 'hitstick', 'hocus','hollyhood',
    'freddy', "friends'll", 'frigidaire', 'fronto', 'fuckboys','fudd', 'gangbanging', 'gasolina', 'getter', 'gilligan', 'gimme','giuseppe','hakuna',
    'droptop', 'dundee', 'dunno', 'dutchies', 'eardrummers','eliott', 'elmer','eres', 'eurostep', 'exposured','fallon', 'fendis', 'ferris','finneran','foo',
    'cinemax', 'cocina','colada','conman', 'coochies','dicking', 'digiorno', 'disect','corella', 'dahmer', 'dang','deebo', 'deng','donatella', 'doobie', 'dookie','dooley', 'doot', 'driz',
    'blasé', 'bmx', 'bobo', 'bonita','brax', 'breitling', 'brokanese','busta','cabo','caine', 'calabasas', 'campos','carlito', 'catfishing', 'chan', 'chapstick', 'chinky', 'cho',
'addys', 'adrien', 'altoid', 'andale', 'anita', 'anyday', 'aston', 'aw', 'backpage', 'backstreets', 'ballenciaga','bama', 'barclays', 'beaucoup','beverly', 'bic', 'bidness', 'blackson',
    'antiqua', "your", "you's", "you're", "wanna", "what", "where", "with", "wouldn't", "y'all", "vvs", "twο", "to", "this", "anytime","them", "these", "they", "the", "that's", "that", "stop", "should", "she's",
    "phantοm", "ours", "our", "kush","know", "jane", "if", "huh", "house", "how", "her", "good", "got", "gucci", "gotta", "gonna", "gon", "fοr","from", "fleek", "ferrari","ferraris", "rari", "everything", "dope", "double", "don't", "do", "cοuldn't", "cost",
    "cοngratulatiοns", "cuz", "cuchi", "closed", "come", "cocaine", "bro", "bentley", "because", "aye", "and", "ain't","vv's",'backburner', 'backdoored', 'backstreet', 'backwood', 'ballerific', 'beamer',
    "aquafina", "finna", "she", "of", "off", "out", "cost", "ah", "aka", "bruh", "bentelys", "blinging",'acapella','addy', 'africano', 'akmaui','billi','budweiser','cal', 'camaro','chaingang',
    "bubba", "cannot", "could", "cowabunga", "everybody", "everyone", "for", "flosser", "geeking", "gimmie",'um', 'vicodins','avion','benzes','berettas', 'betta', 'bg', 'bicoastal', 'biggie',
    "him", "hers", "homecooking", "homies", "i'm", "i'ma", "into", "isn't", "i've", "jocking", "jock","vvs's",'apado', 'apen', 'armani', 'ave','boutta', 'britney','cassidy', 'casted',
    "motherfucking", "my", "myself", "nah", "nuff", "oh", "og", "piccadilly", "pittsburg", "porsche", "psyche",'birkins','birkin', 'biscayne', 'blicky', 'bo', 'bodago', 'bonjour', "boo'd", 'boogieman',
    "rehab", "shaq", "shawty", "starburst", "stupider", "than", "those", "wanna", "wasn't", "we've", "when", "you",'vuitton','aventadors','aventador','clayco', 'cocaina','colorblind', 'conversate',
    "yourself", "yo", "what's", "choppa", "colombine", "lil", "legit", "uno", "unless", "wassup", "tryna", "thugging",'conversating', 'convo', 'courtside', 'creme', 'cuatro', 'culking',
    "adderall", 'against', 'aight','anybody', 'anything', 'anytime','backflip', 'ballers', 'baller','bando','benz','brr','cumming', 'céline','dhabi', 'dixon', 'doja', 'dom','jimi', 'jitsu',
    'beside', 'bio','blowed','boosie', 'bougie','bricked','chanel', 'chia','ciroc', "carrera",'casa', 'chanel','stevie',"you'll", "you've", 'yours', 'ysl','exotics', 'extendo','indo',
    'coulda', "couldn't",'cutie','eigth','escobar','everytime','geeked','girly','giuseppes', 'givenchy','goldie', 'goodie','dranked', 'dranking', 'drexter','goyard', "grammy's", 'griffey',
    'gotti', 'grandaddy','gt','harley','hella', 'herself', 'hey','hiffie', 'homie','illinos','jacky','janet', 'jewelery','duracell','everynight','everyday','flexer', 'forbes', 'foreigns', 'freakazoid', 'freeband',
    'karl', 'kia', 'kim', 'kimbo','lakers', 'lambo', 'lamborghini','lotta', 'louie','mariah', 'mascato', 'matire', 'maybach', 'merk', 'micros','freebands','gonzales','jugg', 'jumanji', 'jumpman',
    'midgrade','miley', 'mitsubishi','ménage', 'multi', 'nickle','nor','outta', 'ow', 'papi','pj','pp', 'prob','prolly','pyro','fabo', 'faceoff', 'facetime', 'fadeaway', 'fanta', 'federales',
    'redded', 'reefa', 'ricky', 'rida', 'riverdale', 'robster','rocko', 'roscoe', 'royce', 'rozay', 'runnie',"swole",'fendi', 'ferragamo', 'fetti', 'finessed', 'finessing', 'fishscale', 'flatline', 'flav',
    'seater', 'sextape', 'shes', 'sho','since','snaggle', 'snorkling','something','stanking', 'stanky','stopsign',"they'll", 'thottie', 'thotties','gallo', 'gambino','jocked', 'joe',
'subaru', 'sucka','susie', 'swayze','telemundo','their', 'theirs','themselves', "there'll","they're", 'thoughta','fro', 'fugazi', 'fuzzing','guala', 'guap','hasta', 'hennessy','lib',
"they're", 'thoughta', 'thowed', 'thrax', 'throwed', 'tiqua','tity', 'tony', 'trans', 'trapstar', 'trois', 'tryna','gabbana','gangbang', 'geezy', 'gelato','jeez','laurent', 'layed', 'leno', 'lesbi', 'lesley',
'until','vert', 'vette', 'vibing','waldorf', 'walkie', 'wasn\'t', 'we','webbie','whatcha', 'whatchu',"where's", 'whether', 'which', 'whoozy','hilton','itself', 'jacoby', 'jal', 'jayhawks',
'without',"ya'll",'ye', "you'd",'hydro','babygirl','bape','beatle', 'benzo', 'bestie', 'bezzel', 'bicurious', 'birdy','booling', 'braxton', 'bugatti','instagram','parkay',
'bustdown','chapo', 'chapos', 'chris', 'chrissy','cripping', "d'ussé",'dennis', "denny's", 'diablo', 'diddy', "didn't",'xan', 'xanny', 'xxl','hublot', 'hublots', 'huncho', 'ibiza',
"dora", "espanol",'floyd', 'foldgers','forgiato', "forgiatos", 'geekers', 'girlies', 'grande', 'gtv','guaped','wamp', 'weegee', 'wendy','glam', 'glock',"ma'am",'mamacitas',
'hallie', 'harambe', 'hefner', 'helluva','henny','iphone', "it'll", 'jalapeño','kawasaki', 'kenny', 'kevin', 'kimosabe', 'kinte','kunta',"ooh",'katy', 'khloe','peyton', 'pg', 'philippe', 'pico',
'lol','maserati', 'mazzi','meagan', 'mercedez', 'micky', 'milli','motherfuck','mula','myspace', 'nerdy','patek', 'pateks', 'percocets', 'killtech', 'kirkland','manolo', 'margiela', 'marta', 'maxed',
'pippen', 'plotty', 'prada', 'pringles','remix', 'rodman', 'rolex', 'rollies','samsung', 'santana', 'scuse', 'seagal', 'sheisty','kardashian','kroger', 'kyrie','mannie',
'sold', 'sony','spreaded', 'stacey',"swagger","swag",'swishers', 'them',"thugger",'timbs','twitpic', 'ty', 'uh','upon', 'vick', 'villian', 'wack', 'waddup','mj', 'moe','perignon',
'wheaties', 'whoa','wifey', 'willie', 'would','yep','youngins','acura', 'akon', 'alicia', 'anyone', 'ap', 'apeshit', 'app', 'arthur', 'as', 'atl', 'audemar', 'audi', 'ayo','prezzies', 'prometh', 'pucci', 'putang',
'balmain', 'balmains','barbie', 'barry', 'beavis', 'becky','benji', 'bih','bentleys', 'beretta', 'biatrice', 'bieber','birdman', 'bity', 'bizzy', 'bleek', 'blocka', 'blouser',
'brazy', 'brian',"brody",'bros', 'brung', 'butthead', "by's", 'caillou', "cam'ron", 'cancún', 'carlo', 'carmelo', 'cavs', 'celine', 'charlie', 'ching','chong', 'cinco','danny',
'claus', "could've",'diggy', "dillard's",'discriminize',"doesn't", 'donald', 'dopeboy','dr','elliantte', 'elliott', 'else', 'endo','fam', 'familia','fn', "folger's", 'forgis', 'forreal',
'frito', 'fuckboy',  'glover', 'godzilla', 'goodfellas', 'hannah', 'hashtag', 'hbo', 'heh','grinch','gwaluh','hokus', "homies", 'honda','jeffery', 'jetskis', 'jetson', 'juan', 'julio', 'justin', 'juug','keisha', 'kemosabe', 'kensli', 'kenzo',
'khalifa', 'klumps','knick', 'knicks','lemme', 'lightskin', 'lorenzos', 'losie', 'loubs', 'lucci', 'lukemi','malcom', 'maliah', 'malo', 'mamacita', 'margielas', 'mase', 'maury', 'mayweather', 'mcdonalds', 'mcknight', 'meechy', 'meech','migo', 'milly', 'mmm', 'monique', 'moonrock',
"motherfuckers", "motherfuck", "motherfucking", "must've", 'mysterio','nana', 'nascar','nba','nother','oops', 'osama', 'ostritch', 'others', 'overexaggerating', 'oxycontin','panamera', 'passcode', 'patrón','popeye', 'prepping', 'psh', 'punchanella', 'purp',
'quan','pillies', 'rahul', 'ralo', 'ramen', 'reagles', 'remy', 'repped','rollercoast', 'rollie', 'ruger', 'rwar','scooby', 'scotty', 'scroller','sheesh', 'shitted', 'shotta',"should've", "shouldn't", 'shoutout', 'simmons',
 'snoop',"scoob",'skype',"spaz",'timeout', 'tock', 'tommy', 'tootsie', 'trillest','maxing', 'maybelline', 'mcgrady', 'mercedes', 'merch', 'mets', 'migliano', 'migos', 'mixtapes',
'moonwalking', 'mossberg',"motivation'll", 'mufasa','mufasa','mulsanne', 'mustafa', 'mutombo', 'myers','nat', 'neglection', 'nelly','nfl','nintendo','nobu','ought', 'pablo', 'pacino',
    'pacquiao','peachtree', 'percocet','pornstar', 'porsches', 'pre','rari', 'raris','queso','skrrt','reeboks', 'reggie', 'regis','rillo', 'rillos','xannies', 'xans',
'yayo','yolanda', 'yopper', 'yucatán',"would've", 'woulda',"vv's",'vv','wifeys','whoopi', 'weezy', "whatever's", 'whenever', 'whew', 'whoever', 'whoo','wacked', 'turbo',
'turnt','tenderoni', 'texting', "that'll", 'theodore', "they'd", 'thot', 'tiarra', 'traphouse','tribeca', 'tropicana',"vroom",'splain','slatt', 'slutty', 'snapchat',
]

def is_slang(word: str):
    """checks to see if word exists """
    if len(word) == 1 and word != 'i' and word != 'a' and word != 'g' and word != 'b' and\
            word != 'd' and word != "e" and word != "j" and word != "k" and word != "x" and word != "p":
        return False
    if hasNumbers(word):
        return True
    for item in ok_slang:
        if word == item:
            return False
    word = word.replace("\'", "")
    return (str(dictionary.meaning(word))[:4]=="None")

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def insert_word(word: str):
    """Inserts all the proper words as individual items into the database and slang words into a list"""

    response = word_table.get_item(
        Key={
            'id': word
        }
    )
    if 'Item' not in response:
        print("{} not in database".format(word))
        word_table.put_item(
            Item={
                'id': word
            }
        )
    else:
        print("{} already in database".format(word))
def get_slang_list():
    response = word_table.get_item(
        Key={
            'id': "slang_words"
        }
    )
    slang_list = list(response['Item']['words'])
    return (slang_list)

for word in slang_words:
    word = clean_slang(word)
    if is_slang(word) is False:
        insert_word(word)
#print(is_slang("morphine"))
