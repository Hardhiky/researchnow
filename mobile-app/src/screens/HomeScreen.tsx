/**
 * HomeScreen.tsx
 * Main home screen for ResearchNow mobile app
 * Features: Search, trending papers, recent papers
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

interface Paper {
  id: number;
  title: string;
  authors: string[];
  abstract: string;
  citationCount: number;
  publicationYear: number;
  fieldOfStudy: string[];
  isOpenAccess: boolean;
}

const HomeScreen = () => {
  const navigation = useNavigation();
  const [searchQuery, setSearchQuery] = useState('');
  const [trendingPapers, setTrendingPapers] = useState<Paper[]>([]);
  const [recentPapers, setRecentPapers] = useState<Paper[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Mock data - replace with actual API calls
  const mockPapers: Paper[] = [
    {
      id: 1,
      title: 'Attention Is All You Need',
      authors: ['Vaswani et al.'],
      abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...',
      citationCount: 85420,
      publicationYear: 2017,
      fieldOfStudy: ['Computer Science', 'Machine Learning'],
      isOpenAccess: true,
    },
    {
      id: 2,
      title: 'Deep Residual Learning for Image Recognition',
      authors: ['He et al.'],
      abstract: 'Deeper neural networks are more difficult to train. We present a residual learning framework...',
      citationCount: 142380,
      publicationYear: 2015,
      fieldOfStudy: ['Computer Science', 'Computer Vision'],
      isOpenAccess: true,
    },
    {
      id: 3,
      title: 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
      authors: ['Devlin et al.'],
      abstract: 'We introduce a new language representation model called BERT...',
      citationCount: 67234,
      publicationYear: 2018,
      fieldOfStudy: ['Computer Science', 'NLP'],
      isOpenAccess: true,
    },
  ];

  const categories = [
    { icon: 'all-inclusive', label: 'All' },
    { icon: 'laptop', label: 'CS' },
    { icon: 'atom', label: 'Physics' },
    { icon: 'flask', label: 'Chemistry' },
    { icon: 'dna', label: 'Biology' },
    { icon: 'calculator', label: 'Math' },
    { icon: 'hospital', label: 'Medicine' },
  ];

  useEffect(() => {
    fetchTrendingPapers();
    fetchRecentPapers();
  }, []);

  const fetchTrendingPapers = async () => {
    // TODO: Replace with actual API call
    setTrendingPapers(mockPapers);
  };

  const fetchRecentPapers = async () => {
    // TODO: Replace with actual API call
    setRecentPapers(mockPapers);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchTrendingPapers(), fetchRecentPapers()]);
    setRefreshing(false);
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigation.navigate('Search' as never, { query: searchQuery } as never);
    }
  };

  const handlePaperPress = (paperId: number) => {
    navigation.navigate('PaperDetail' as never, { paperId } as never);
  };

  const renderPaperCard = ({ item }: { item: Paper }) => (
    <TouchableOpacity
      style={styles.paperCard}
      onPress={() => handlePaperPress(item.id)}
      activeOpacity={0.7}
    >
      <View style={styles.paperHeader}>
        <View style={styles.paperBadge}>
          {item.isOpenAccess && (
            <View style={styles.openAccessBadge}>
              <Icon name="lock-open-variant" size={12} color="#10b981" />
              <Text style={styles.openAccessText}>Open Access</Text>
            </View>
          )}
        </View>
        <Text style={styles.paperYear}>{item.publicationYear}</Text>
      </View>

      <Text style={styles.paperTitle} numberOfLines={2}>
        {item.title}
      </Text>

      <Text style={styles.paperAuthors} numberOfLines={1}>
        {item.authors.join(', ')}
      </Text>

      <Text style={styles.paperAbstract} numberOfLines={2}>
        {item.abstract}
      </Text>

      <View style={styles.paperFooter}>
        <View style={styles.paperTags}>
          {item.fieldOfStudy.slice(0, 2).map((field, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{field}</Text>
            </View>
          ))}
        </View>
        <View style={styles.citationBadge}>
          <Icon name="format-quote-close" size={14} color="#6b7280" />
          <Text style={styles.citationText}>
            {item.citationCount.toLocaleString()}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderCategoryItem = (category: { icon: string; label: string }) => (
    <TouchableOpacity
      key={category.label}
      style={[
        styles.categoryButton,
        selectedCategory === category.label && styles.categoryButtonActive,
      ]}
      onPress={() => setSelectedCategory(category.label)}
    >
      <Icon
        name={category.icon}
        size={20}
        color={selectedCategory === category.label ? '#3b82f6' : '#6b7280'}
      />
      <Text
        style={[
          styles.categoryLabel,
          selectedCategory === category.label && styles.categoryLabelActive,
        ]}
      >
        {category.label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Header */}
        <LinearGradient
          colors={['#3b82f6', '#8b5cf6']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <View style={styles.logoContainer}>
              <Icon name="book-open-page-variant" size={32} color="#fff" />
              <Text style={styles.logoText}>ResearchNow</Text>
            </View>
            <TouchableOpacity style={styles.notificationButton}>
              <Icon name="bell-outline" size={24} color="#fff" />
              <View style={styles.notificationDot} />
            </TouchableOpacity>
          </View>

          {/* Search Bar */}
          <View style={styles.searchContainer}>
            <Icon name="magnify" size={24} color="#6b7280" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search papers, authors, DOI..."
              placeholderTextColor="#9ca3af"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
              returnKeyType="search"
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')}>
                <Icon name="close-circle" size={20} color="#9ca3af" />
              </TouchableOpacity>
            )}
          </View>

          {/* Stats */}
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>200M+</Text>
              <Text style={styles.statLabel}>Papers</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>8</Text>
              <Text style={styles.statLabel}>Sources</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>50M+</Text>
              <Text style={styles.statLabel}>Full Texts</Text>
            </View>
          </View>
        </LinearGradient>

        {/* Categories */}
        <View style={styles.categoriesSection}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoriesContainer}
          >
            {categories.map(renderCategoryItem)}
          </ScrollView>
        </View>

        {/* Trending Papers */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleContainer}>
              <Icon name="trending-up" size={24} color="#f59e0b" />
              <Text style={styles.sectionTitle}>Trending Now</Text>
            </View>
            <TouchableOpacity onPress={() => navigation.navigate('Trending' as never)}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={trendingPapers}
            renderItem={renderPaperCard}
            keyExtractor={(item) => item.id.toString()}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.papersList}
          />
        </View>

        {/* Recent Papers */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={styles.sectionTitleContainer}>
              <Icon name="clock-outline" size={24} color="#3b82f6" />
              <Text style={styles.sectionTitle}>Recently Added</Text>
            </View>
            <TouchableOpacity onPress={() => navigation.navigate('Recent' as never)}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>

          {recentPapers.map((paper) => (
            <View key={paper.id}>
              {renderPaperCard({ item: paper })}
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity style={styles.quickActionCard}>
              <Icon name="bookmark-outline" size={32} color="#3b82f6" />
              <Text style={styles.quickActionText}>Bookmarks</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickActionCard}>
              <Icon name="folder-outline" size={32} color="#8b5cf6" />
              <Text style={styles.quickActionText}>Collections</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickActionCard}>
              <Icon name="history" size={32} color="#10b981" />
              <Text style={styles.quickActionText}>History</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickActionCard}>
              <Icon name="cog-outline" size={32} color="#f59e0b" />
              <Text style={styles.quickActionText}>Settings</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 30,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginLeft: 12,
  },
  notificationButton: {
    position: 'relative',
  },
  notificationDot: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ef4444',
    borderWidth: 2,
    borderColor: '#fff',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchIcon: {
    marginRight: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 16,
    paddingVertical: 12,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  statLabel: {
    fontSize: 12,
    color: '#e0e7ff',
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  categoriesSection: {
    marginTop: 20,
  },
  categoriesContainer: {
    paddingHorizontal: 20,
  },
  categoryButton: {
    alignItems: 'center',
    marginRight: 20,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  categoryButtonActive: {
    backgroundColor: '#eff6ff',
    borderColor: '#3b82f6',
  },
  categoryLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6b7280',
    marginTop: 4,
  },
  categoryLabelActive: {
    color: '#3b82f6',
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginLeft: 8,
  },
  seeAllText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '600',
  },
  papersList: {
    paddingBottom: 8,
  },
  paperCard: {
    width: width - 80,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginRight: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  paperHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  paperBadge: {
    flex: 1,
  },
  openAccessBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#d1fae5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  openAccessText: {
    fontSize: 10,
    color: '#059669',
    fontWeight: '600',
    marginLeft: 4,
  },
  paperYear: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '500',
  },
  paperTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8,
    lineHeight: 22,
  },
  paperAuthors: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  paperAbstract: {
    fontSize: 13,
    color: '#4b5563',
    lineHeight: 20,
    marginBottom: 12,
  },
  paperFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  paperTags: {
    flexDirection: 'row',
    flex: 1,
  },
  tag: {
    backgroundColor: '#eff6ff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginRight: 6,
  },
  tagText: {
    fontSize: 11,
    color: '#3b82f6',
    fontWeight: '500',
  },
  citationBadge: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  citationText: {
    fontSize: 12,
    color: '#6b7280',
    marginLeft: 4,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  quickActionCard: {
    width: (width - 60) / 2,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginTop: 8,
  },
});

export default HomeScreen;
