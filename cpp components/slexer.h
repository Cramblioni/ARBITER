#pragma once
#include <string>
#include <iostream>


class Token
{
public:
	enum class Kind
	{
		ident, // examples:: set,create,if
		number,
		string,
		plus, minus, aster, fslsh, // arithmatic operators
		oppar, clpar, // open parenthesis and close
		ocb, ccb, // [ and ]
		equ, gth, lth,
		URT,eof
	};

	Token(Kind kind) noexcept :m_kind{ kind } {}
	Token(Kind kind, std::string intern) noexcept : m_kind{ kind }, m_lexeme{ intern } {}
	Token(Kind kind, const char* strt, const char* end) noexcept : m_kind{ kind }, m_lexeme{ strt,std::distance(strt,end) } {} // because sheit
	Token(Kind kind, const char* strt, int len) noexcept : m_kind{ kind }, m_lexeme{ strt,len} {} 
	Kind kind() noexcept { return m_kind; } // for once getter/setter might make this easier
	std::string lexeme() noexcept { return m_lexeme; }
	void kind(Kind kind) noexcept { m_kind = kind; } // for once getter/setter might make this easier
	void lexeme(std::string lexeme) noexcept { m_lexeme = lexeme; }
	bool is(Kind kind) const noexcept { return m_kind == kind; }
private:
	Kind m_kind{};
	std::string m_lexeme; // i think that's the name of it
};
bool isDigit(char c) {
	return (c >= 48) && (c <= 57);
}
bool isAlpha(char c)
{
	c &= 223; return (c >= 65) && (c <= 90);
}
bool isWhite(char c)
{
	return (c == ' ') || (c == '\t') || (c == '\n') || (c == '\r');
}
class Lexer
{
private:
	const char* front = nullptr;
	char peek() { return *front; }
	char next() { return *front++; }
	
	Token getIdent() {
		const char* strt = front;
		while (isAlpha(peek())) next();
		return Token(Token::Kind::ident, strt,front);
	}
	Token getNumber()
	{
		const char* tmp = front; bool hdp = false;
		
		while ( ( isDigit(peek()) || peek() == '.') )
		{
			if (peek() == '.') 
				{ if (hdp) break; else {hdp = true; } }
			next();
		}
		return Token(Token::Kind::number, tmp,front);
	}
	Token getString()
	{
		const char* tmp = ++front;
		while (peek() != '"') next();
		return Token(Token::Kind::string, tmp, front++ );
	}
	
public:
	Lexer(const char* text) noexcept: front{ text } {}
	Lexer(char* text) noexcept :front{ text } {}
	
	Token Next()
	{
		while (isWhite(peek())) next();
		char cc = peek();
		if (isAlpha(cc)) return getIdent();
		else if (cc == '#') { next(); while (peek() != '#') next();next(); return Next(); }
		else if (isDigit(cc)) return getNumber();
		else if (cc == 0) return Token(Token::Kind::eof);
		else switch (cc)
		{
		case '"': return getString();

		case '+':return Token(Token::Kind::plus,	 front++, 1);
		case '-':return Token(Token::Kind::minus,	 front++, 1);
		case '*':return Token(Token::Kind::aster,	 front++, 1);
		case '/':return Token(Token::Kind::fslsh,	 front++, 1);

		case '(':return Token(Token::Kind::oppar,	 front++, 1);
		case ')':return Token(Token::Kind::clpar,	 front++, 1);
		case '[':return Token(Token::Kind::ocb,		 front++, 1);
		case ']':return Token(Token::Kind::ccb,		 front++, 1);

		case '=':return Token(Token::Kind::equ,		 front++, 1);
		case '>':return Token(Token::Kind::gth,		 front++, 1);
		case '<':return Token(Token::Kind::lth,		 front++, 1);

		case 0:return Token(Token::Kind::eof);
		default: return Token(Token::Kind::URT,		 front++,1);
		}
		
	}
};


// This is so i can print out some the lexed tokens with ease
std::ostream& operator<<(std::ostream& os, const Token::Kind& kind) {
	static const char* const names[]{
		"ident", 
		"number",
		"string",
		"plus", "minus", "asterisk", "forward slash", 
		"open paren", "close paren", 
		"op codbod", "close codbod",
		"equals", "greater than", "less than",
		"unrecognised","eof"
	};
	return os << names[static_cast<int>(kind)];
}