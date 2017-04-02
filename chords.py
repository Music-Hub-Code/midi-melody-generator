import collections
import copy
import random

from melody_properties import MelodyProperties
from pyknon.music import NoteSeq, Note, Rest


class Chord(NoteSeq):
    def __init__(self, args, first_note=None, name=None):
        NoteSeq.__init__(self, args=args)
        if isinstance(first_note, Note):
            self.first_note = first_note
        elif first_note is None:
            self.first_note = self.items[0]

        if name is None:
            self.name = self.first_note.name
        else:
            self.name = name

    def outside(self):
        return NoteSeq([self.items[0]] + [self.items[-1]])

    def inside(self):
        middle = float(len(self.items)) / 2
        if middle % 2 != 0:
            return NoteSeq([self.items[int(middle - .5)]])
        else:
            return NoteSeq([self.items[int(middle - 1)], self.items[int(middle)]])

    def bottom(self):
        return NoteSeq([self.items[0]])

    def top(self):
        return NoteSeq(self.items[1:])

    def inversion(self, index=0):
        inversion = copy.deepcopy(self.items)
        first_note = inversion.pop(0)
        inversion.append(first_note.octave_shift(1))
        return Chord(inversion, first_note=self.first_note, name=self.name + "-inversion")

    def stretch_dur(self, factor):
        return Chord(NoteSeq.stretch_dur(self, factor).items, first_note=self.first_note, name=self.name)

    def octave_shift(self, octaves):
        return Chord(NoteSeq.octave_shift(self, octaves).items, first_note=self.first_note,
                     name=self.name + "-octave_shift(" + str(octaves) + ")")


class Chords:
    silence = Chord([Rest()], name="Silence")

    # Major key
    I = Maj1 = Chord("C   E   G  ", name="I")
    ii = min2 = Chord("D   F   A  ", name="ii")
    iii = min3 = Chord("E   G   B  ", name="iii")
    IV = Maj4 = Chord("F   A   C''", name="IV")
    V = Maj5 = Chord("G   B   D''", name="V")
    vi = min6 = Chord("A   C'' E  ", name="vi")
    vii = dim7 = Chord("B   D'' F  ", name="vii")

    # Minor key
    I_min_key = Chord("C   D#   G  ", name="I_min_key")
    ii_min_key = Chord("D   F   G#  ", name="ii_min_key")
    iii_min_key = Chord("D#   G   A#  ", name="iii_min_key")
    IV_min_key = Chord("F   G#   C''", name="IV_min_key")
    V_min_key = Chord("G   A#   D''", name="V_min_key")
    vi_min_key = Chord("G#   C'' D#  ", name="vi_min_key")
    vii_min_key = Chord("A#   D'' F  ", name="vii_min_key")

    major_scale = [I, I.inversion(), I.inversion().inversion(), I.octave_shift(1), I.octave_shift(-1),
                   ii, iii, IV, V, vi]  # happy
    minor_scale = [I_min_key, I_min_key, I_min_key.inversion(), I_min_key.inversion().inversion(),
                   I_min_key.octave_shift(1), I_min_key.octave_shift(-1),
                   ii_min_key, iii_min_key, IV_min_key, V_min_key, vi_min_key]  # sad
    mixed_scale = major_scale + minor_scale

    # for chord progression:
    chord_prog_first = [I, I.inversion(), I.inversion().inversion(), I.octave_shift(1), I.octave_shift(-1),
                        I_min_key, I_min_key.inversion(), I_min_key.inversion().inversion(),
                        I_min_key.octave_shift(1), I_min_key.octave_shift(-1)]
    chord_prog_middle = [ii, ii_min_key, iii, iii_min_key, IV, IV_min_key, V, V_min_key, vi, vi_min_key]
    chord_prog_last = [IV, IV_min_key, V, V_min_key]


class ChordSeq(collections.MutableSequence):
    def __init__(self, mood=None, chords=None):
        if mood is None:
            self.mood = random.choice(list(MelodyProperties.Moods))
        elif isinstance(mood, MelodyProperties.Moods):
            self.mood = mood
        else:
            raise AttributeError("ChordSeq doesn't accept this type of data.")

        if isinstance(chords, collections.Iterable):
            self.chords = chords
        elif chords is None:
            self.chords = self._generate_chord_progression()
        else:
            raise AttributeError("ChordSeq doesn't accept this type of data.")

    def __iter__(self):
        for x in self.chords:
            yield x

    def __delitem__(self, i):
        del self.chords[i]

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.chords[i]
        else:
            return ChordSeq(self.chords[i])

    def __len__(self):
        return len(self.chords)

    def __setitem__(self, i, value):
        self.chords[i] = value

    def __repr__(self):
        return "<Seq: {0}>".format(self.chords)

    def __eq__(self, other):
        if len(self) == len(other):
            return all(x == y for x, y in zip(self.chords, other.chords))

    def __add__(self, other):
        return ChordSeq(chords=self.chords + other.chords)

    def __mul__(self, n):
        return ChordSeq(chords=self.chords * n)

    @property
    def verbose(self):
        string = ", ".join([chord.name for chord in self.chords])
        return "<ChordSeq: [{0}]>".format(string)

    def _generate_chord_progression(self):
        if self.mood == MelodyProperties.Moods.HAPPY:
            chord_scale = Chords.major_scale
        elif self.mood == MelodyProperties.Moods.SAD:
            chord_scale = Chords.minor_scale
        else:
            chord_scale = Chords.mixed_scale

        # chord progression starts with chord I, ends with chord IV or V and has other chords between
        first_chord = random.sample(set(Chords.chord_prog_first).intersection(chord_scale), 1)[0]
        last_chord = random.sample(set(Chords.chord_prog_last).intersection(chord_scale), 1)[0]

        # Choose 2 middle chords from list which does not contain last_chord
        middle_chords_set = copy.copy(Chords.chord_prog_middle)
        middle_chords_set.remove(last_chord)
        middle_chords_set = set(middle_chords_set).intersection(chord_scale)

        middle_chords = random.sample(middle_chords_set, 2)
        return [first_chord] + middle_chords + [last_chord]

    def octave_shift(self, octave_shift):
        return ChordSeq(chords=[chord.octave_shift(octave_shift) for chord in self])

    def insert(self, i, value):
        self.chords.insert(i, value)
